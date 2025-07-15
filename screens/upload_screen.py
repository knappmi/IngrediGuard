from screens.base_screen import BaseScreen
from utils.menu_parser import parse_menu_file
from utils.menu_parser import parse_menu_stream
from utils.feature_flags import OCR_ENABLED

# Conditional import: only bring in the heavy OCR module when the feature flag is enabled.
if OCR_ENABLED:
    from utils.ocr_api import extract_menu_from_image
else:
    def extract_menu_from_image(*_args, **_kwargs):
        return None

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.logger import Logger
from jnius import autoclass, cast
import os
import csv
import time
from io import StringIO
import platform
# from opentelemetry import trace
from utils.error_handler import error_handler

if platform == 'android':
    from android import mActivity
    Intent = autoclass('android.content.Intent')
    File = autoclass('java.io.File')
    Uri = autoclass('android.net.Uri')
    FileProvider = autoclass('androidx.core.content.FileProvider')

class UploadScreen(BaseScreen):
    def __init__(self, **kwargs):
        """Upload Screen for menu file upload and OCR."""
        # self.tracer = trace.get_tracer(__name__)
        Logger.info("[UploadScreen] Initializing Upload Screen")
        super().__init__(**kwargs)

        Logger.info("UploadScreen: Initializing UploadScreen")
        
        button_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        self.select_button = Button(text='Select File', size_hint_x=0.5)
        self.select_button.bind(on_press=self.open_filechooser)
        button_row.add_widget(self.select_button)
        
        # Only show the camera capture option when OCR functionality is
        # enabled via the global feature flag.
        if OCR_ENABLED:
            self.camera_button = Button(text='Capture Menu Photo', size_hint_x=0.5)
            self.camera_button.bind(on_press=self.capture_photo)
            button_row.add_widget(self.camera_button)
        
        self.layout.add_widget(button_row)
        Logger.info("UploadScreen: File selection buttons added")

        self.preview_container = BoxLayout(orientation='vertical', size_hint_y=None)
        self.preview_container.bind(minimum_height=self.preview_container.setter('height'))
        
        self.preview_area = ScrollView(size_hint=(1, 0.4))
        self.preview_area.add_widget(self.preview_container)
        self.layout.add_widget(self.preview_area)
        Logger.info("UploadScreen: Preview area added")

        button_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=110)
        
        self.upload_button = Button(text='Preview Menu File', size_hint_y=None, height=50)
        self.upload_button.bind(on_press=self.load_menu)
        self.upload_button.disabled = True
        button_layout.add_widget(self.upload_button)
        Logger.info("UploadScreen: Upload button added")

        self.confirm_button = Button(text='Confirm and Save', size_hint_y=None, height=50)
        self.confirm_button.bind(on_press=self.confirm_menu)
        self.confirm_button.disabled = True
        button_layout.add_widget(self.confirm_button)
        Logger.info("UploadScreen: Confirm button added")

        self.layout.add_widget(button_layout)

        self.selected_uri = None
        self.image_path = None
        self.parsed_menu_data = None
        self.is_ocr_mode = False

        self.bind(manager=self._set_back_button)
        Logger.info("UploadScreen: UploadScreen initialized")

    @error_handler
    def open_filechooser(self, instance):
        Logger.info("UploadScreen: Opening native file picker")
        from android import activity
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE])

        Intent = autoclass('android.content.Intent')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity_instance = PythonActivity.mActivity

        intent = Intent(Intent.ACTION_GET_CONTENT)
        intent.setType("*/*")
        activity_instance.startActivityForResult(intent, 1001)

        activity.bind(on_activity_result=self.on_activity_result)
        self.is_ocr_mode = False

    @error_handler
    def capture_photo(self, instance):
        """Capture a photo using the camera with proper FileProvider implementation."""
        # with self.tracer.start_as_current_span("upload_screen.capture_photo") as span:
        #     span.set_attribute("is_ocr_mode", self.is_ocr_mode)
            
        Logger.info("UploadScreen: Opening camera for menu capture")
        from android import activity
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.CAMERA,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])

        # Create app-specific directory for photos if it doesn't exist
        photo_dir = os.path.join(os.getcwd(), "app_data", "photos")
        os.makedirs(photo_dir, exist_ok=True)
        
        # Create a unique filename with timestamp
        timestamp = int(time.time())
        self.image_path = os.path.join(photo_dir, f"menu_photo_{timestamp}.jpg")
        Logger.info(f"UploadScreen: Photo will be saved to {self.image_path}")

        Intent = autoclass('android.content.Intent')
        MediaStore = autoclass('android.provider.MediaStore')
        File = autoclass('java.io.File')
        Uri = autoclass('android.net.Uri')
        FileProvider = autoclass('androidx.core.content.FileProvider')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        PackageManager = autoclass('android.content.pm.PackageManager')
        
        activity_instance = PythonActivity.mActivity
        
        # Create a file for the photo
        file = File(self.image_path)
        
        # Get content URI using FileProvider
        package_name = activity_instance.getPackageName()
        photo_uri = FileProvider.getUriForFile(
            activity_instance, 
            f"{package_name}.fileprovider", 
            file
        )
        
        # Create camera intent
        intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        intent.putExtra(MediaStore.EXTRA_OUTPUT, photo_uri)
        
        # Grant URI permissions to the camera app
        camera_package = "com.android.camera"  # Default camera package
        try:
            # Try to get the default camera app
            pm = activity_instance.getPackageManager()
            camera_intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            camera_resolve = pm.resolveActivity(camera_intent, PackageManager.MATCH_DEFAULT_ONLY)
            if camera_resolve:
                camera_package = camera_resolve.activityInfo.packageName
        except Exception as e:
            Logger.warning(f"UploadScreen: Could not determine camera package, using default: {e}")
        
        # Grant permissions to the camera app
        activity_instance.grantUriPermission(
            camera_package,
            photo_uri,
            Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
        )
        
        # Start the camera activity
        activity_instance.startActivityForResult(intent, 1002)
        
        # Bind the result
        activity.bind(on_activity_result=self.on_camera_result)
        self.is_ocr_mode = True

    @error_handler
    def on_camera_result(self, request_code, result_code, intent):
        """Handle the result from the camera activity."""
        # with self.tracer.start_as_current_span("upload_screen.camera_result") as span:
        #     span.set_attribute("request_code", request_code)
        #     span.set_attribute("result_code", result_code)
            
        Logger.info("UploadScreen: Camera activity result received")
        if request_code == 1002:
            # Revoke the URI permissions we granted
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity_instance = PythonActivity.mActivity
                File = autoclass('java.io.File')
                FileProvider = autoclass('androidx.core.content.FileProvider')
                Uri = autoclass('android.net.Uri')
                
                file = File(self.image_path)
                package_name = activity_instance.getPackageName()
                photo_uri = FileProvider.getUriForFile(
                    activity_instance,
                    f"{package_name}.fileprovider",
                    file
                )
                
                activity_instance.revokeUriPermission(
                    photo_uri,
                    Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                )
            except Exception as e:
                Logger.warning(f"UploadScreen: Error revoking URI permissions: {e}")
            
            if result_code == -1:  # RESULT_OK
                Logger.info("UploadScreen: Camera capture successful")
                self.on_camera_success(self.image_path)
            else:
                Logger.warning("UploadScreen: Camera capture cancelled or failed")
                self.on_camera_error("Camera capture was cancelled")

    @error_handler
    def on_camera_success(self, path):
        # with self.tracer.start_as_current_span("upload_screen.on_camera_success") as span:
        Logger.info(f"UploadScreen: Camera capture successful, image saved to {path}")
        self.set_status("Photo captured. Processing with OCR...")
        self.upload_button.disabled = False

    @error_handler
    def on_camera_error(self, error):
        # with self.tracer.start_as_current_span("upload_screen.on_camera_error") as span:
        Logger.warning(f"UploadScreen: Camera capture failed: {error}")
        self.set_status(f"Photo capture failed: {error}")
        self.image_path = None

    @error_handler
    def capture_photo_original(self, instance):
        # with self.tracer.start_as_current_span("upload_screen.capture_photo_original") as span:
        #     span.set_attribute("instance", instance)

        Logger.info("UploadScreen: Starting camera capture")
        Logger.info("UploadScreen: Opening camera for menu capture (original method)")
        from android import activity
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.CAMERA,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])

        # Create app-specific directory for photos if it doesn't exist
        photo_dir = os.path.join(os.getcwd(), "app_data", "photos")
        os.makedirs(photo_dir, exist_ok=True)
        
        # Create a unique filename with timestamp
        timestamp = int(time.time())
        self.image_path = os.path.join(photo_dir, f"menu_photo_{timestamp}.jpg")
        Logger.info(f"UploadScreen: Photo will be saved to {self.image_path}")

        Intent = autoclass('android.content.Intent')
        MediaStore = autoclass('android.provider.MediaStore')
        File = autoclass('java.io.File')
        Uri = autoclass('android.net.Uri')
        FileProvider = autoclass('androidx.core.content.FileProvider')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Environment = autoclass('android.os.Environment')
        
        activity_instance = PythonActivity.mActivity
        
        # Create a file for the photo
        file = File(self.image_path)
        
        # Get content URI using FileProvider
        package_name = activity_instance.getPackageName()
        photo_uri = FileProvider.getUriForFile(
            activity_instance, 
            f"{package_name}.fileprovider", 
            file
        )
        
        # Create camera intent
        intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        intent.putExtra(MediaStore.EXTRA_OUTPUT, photo_uri)
        
        # Grant write permission to the intent
        intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
        
        # Start the camera activity
        activity_instance.startActivityForResult(intent, 1002)
        
        # Bind the result
        activity.bind(on_activity_result=self.on_camera_result)
        self.is_ocr_mode = True

    @error_handler
    def on_activity_result(self, request_code, result_code, intent):
        # with self.tracer.start_as_current_span("upload_screen.on_activity_result") as span:
        #     span.set_attribute("request_code", request_code)
        #     span.set_attribute("result_code", result_code)
        #     span.set_attribute("intent", intent)

        Logger.info("UploadScreen: on_activity_result triggered (test)")
        if request_code == 1001 and intent:
            uri = intent.getData()
            if uri:
                Logger.info(f"[UploadScreen: URI received] {uri}")
                self.selected_uri = uri
                self.upload_button.disabled = False
            else:
                Logger.warning("UploadScreen: URI was null")

    @error_handler
    def on_pre_enter(self):
        # with self.tracer.start_as_current_span("upload_screen.on_pre_enter") as span:
        self.confirm_button.disabled = True
        self.upload_button.disabled = True
        Logger.info("UploadScreen: UploadScreen is loading")
        self.clear_preview()
        self.set_status('')

    @error_handler
    def load_menu(self, instance):
        # with self.tracer.start_as_current_span("upload_screen.load_menu") as span:
        #     span.set_attribute("is_ocr_mode", self.is_ocr_mode)

        if self.is_ocr_mode and self.image_path:
            # Only attempt OCR processing when the feature is turned on.
            if OCR_ENABLED:
                self.load_menu_from_image()
            else:
                Logger.info("UploadScreen: OCR is disabled; skipping image processing.")
                self.set_status("OCR feature is disabled.")
        elif self.selected_uri:
            self.load_menu_from_file()
        else:
            Logger.info("UploadScreen: No file or image selected.")
            self.set_status("No file or image selected.")

    @error_handler
    def load_menu_from_image(self):
        if not OCR_ENABLED:
            self.set_status("OCR feature is disabled.")
            return
        # with self.tracer.start_as_current_span("upload_screen.load_menu_from_image") as span:
        #     span.set_attribute("image_path", self.image_path)

        try:
            self.set_status("Processing image with OCR...")
            Logger.info(f"UploadScreen: Processing image with OCR: {self.image_path}")
        
            # Extract menu text from image using OCR
            csv_text = extract_menu_from_image(self.image_path)
            if not csv_text:
                self.set_status("OCR processing failed. Check API key and try again.")
                return
                
            Logger.info(f"UploadScreen: OCR extraction successful. CSV data length: {len(csv_text)}")
            
            # Parse the extracted CSV text
            menu_data = parse_menu_stream(StringIO(csv_text))
            
            if not menu_data:
                Logger.info("UploadScreen: No data parsed from OCR result.")
                self.set_status("No menu data could be extracted from the image.")
                return
                
            self.manager.menu_df = menu_data
            self.parsed_menu_data = menu_data
            self.set_status(f"Extracted {len(menu_data)} menu items from image")
            self.show_preview(menu_data)
            self.confirm_button.disabled = False
        
        except Exception as e:
            import traceback
            Logger.exception(f"UploadScreen: Error processing OCR: {str(e)}")
            print(traceback.format_exc())
            self.set_status(f"Error: {str(e)}")

    @error_handler
    def load_menu_from_file(self):
        # with self.tracer.start_as_current_span("upload_screen.load_menu_from_file") as span:
        if not self.selected_uri:
            Logger.info("UploadScreen: No file selected.")
            self.set_status("No file selected.")
            return

        try:
            Logger.info("UploadScreen: Attempting to read from URI")
            csv_text = self.read_text_from_uri(self.selected_uri)

            from io import StringIO
            Logger.info("UploadScreen: Calling parse_menu_stream")
            Logger.info(f"UploadScreen: Raw CSV text preview -- {csv_text[:100]}")
            Logger.info(f"UploadScreen: parse_menu_stream is {parse_menu_stream}")
            menu_data = parse_menu_stream(StringIO(csv_text))
            Logger.info(f"UploadScreen: Parsed menu data -- {menu_data}")
            
            if not menu_data:
                Logger.info("UploadScreen: No data parsed from menu file.")
                self.set_status("No data parsed from menu file.")
                return
            
            Logger.info("UploadScreen: Successfully invoked parse_menu_stream")
            self.manager.menu_df = menu_data
            self.parsed_menu_data = menu_data
            self.set_status(f"Loaded {len(menu_data)} items")
            Logger.info(f"UploadScreen: Loaded menu data (before preview) -- {menu_data}")
            self.show_preview(menu_data)
            self.confirm_button.disabled = False

        except Exception as e:
            import traceback
            Logger.exception(f"UploadScreen: Error loading menu file {str(e)}")
            print(traceback.format_exc())
            self.set_status(str(e))

    def read_text_from_uri(self, uri):
        # with self.tracer.start_as_current_span("upload_screen.read_text_from_uri") as span:
        Logger.info("UploadScreen: Reading CSV text from URI")
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            contentResolver = currentActivity.getContentResolver()

            inputStream = contentResolver.openInputStream(uri)
            Logger.info("UploadScreen: Input stream opened successfully")

            buffer = bytearray()
            byte = inputStream.read()
            while byte != -1:
                buffer.append(byte)
                byte = inputStream.read()

            inputStream.close()
            text = buffer.decode("utf-8").replace('\r\n', '\n').replace('\r', '\n')
            Logger.info(f"UploadScreen: First 100 characters\n{text[:100]}")
            return text
        except Exception as e:
            Logger.exception(f"UploadScreen: Error reading CSV text from URI: {str(e)}")
            raise e

    @error_handler
    def show_preview(self, menu_data):
        # with self.tracer.start_as_current_span("upload_screen.show_preview") as span:
        #     span.set_attribute("menu_data", menu_data)

        Logger.info("UploadScreen: Showing preview of menu data")
        
        if not menu_data:
            Logger.info("UploadScreen: No menu data to preview.")
            self.set_status("No data to preview.")
            return
        Logger.info(f"UploadScreen: Menu data for preview -- {menu_data}")

        preview_lines = []
        for i, row in enumerate(menu_data[:100], 1):
            item = row['item'].strip()
            ingredients = row['ingredients']
            if isinstance(ingredients, list):
                ingredients = ', '.join(ingredients)
            ingredients = ingredients.strip()
            preview_lines.append(f"{i}. [b]{item}[/b]")
            preview_lines.append(f"   Ingredients: {ingredients}")
            preview_lines.append("")  # Add blank line between items
        
        preview_text = "\n".join(preview_lines)
        Logger.info(f"UploadScreen: Preview text -- {preview_text}")
        
        self.preview_container.clear_widgets()
        preview_label = Label(
            text=preview_text,
            size_hint_y=None,
            text_size=(self.preview_container.width - 20, None),
            halign='left',
            valign='top',
            markup=True,
            padding=(10, 10)
        )
        preview_label.bind(
            texture_size=lambda instance, value: setattr(instance, 'height', value[1]),
            width=lambda instance, value: setattr(instance, 'text_size', (value - 20, None))
        )
        self.preview_container.add_widget(preview_label)

    @error_handler
    def confirm_menu(self, instance):
        # with self.tracer.start_as_current_span("upload_screen.confirm_menu") as span:
        #     span.set_attribute("instance", instance)

        if not self.parsed_menu_data:
            Logger.info("UploadScreen: No menu data to save.")
            self.set_status("No data to save.")
            return

        try:
            save_path = os.path.join("app_data", "menu.csv")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["item", "ingredients"])
                for item in self.parsed_menu_data:
                    ingredients = item['ingredients']
                    if isinstance(ingredients, list):
                        ingredients = ', '.join(ingredients)
                    Logger.info(f"UploadScreen: Writing item {item['item']} with ingredients {ingredients}")
                    writer.writerow([item['item'], ingredients])

            self.manager.db.clear_menu()
            self.manager.db.insert_menu(self.parsed_menu_data)
            self.manager.menu_data = self.manager.db.get_menu()
            Logger.info(f"UploadScreen: Saved menu data to {save_path}")
            self.set_status("Menu uploaded and saved successfully.")
            
            self.manager.current = 'admin_hub'
            
        except Exception as e:
            Logger.exception(f"UploadScreen: Error saving menu: {str(e)}")
            self.set_status(f"Error saving menu: {str(e)}")

    @error_handler
    def _set_back_button(self, instance, value):
        # with self.tracer.start_as_current_span("upload_screen._set_back_button") as span:
        Logger.info("UploadScreen: set_back_button called")
        target = "admin_hub" if self.manager and getattr(self.manager, 'is_admin', False) else "landing"
        back_button = Button(text="Back", size_hint_y=None, height=40)
        back_button.bind(on_press=lambda x: setattr(self.manager, 'current', target))
        self.layout.add_widget(back_button)

    @error_handler
    def clear_preview(self):
        """Clear the preview area when leaving the screen."""
        # with self.tracer.start_as_current_span("upload_screen.clear_preview") as span:
        Logger.info(f"UploadScreen: Clearing preview area")
        if hasattr(self, 'preview_container'):
            self.preview_container.clear_widgets()
            empty_label = Label(
                text="",
                size_hint_y=None,
                height=20
            )
            self.preview_container.add_widget(empty_label)

    @error_handler
    def on_leave(self):
        """Clear the status label when leaving the screen."""
        # with self.tracer.start_as_current_span("upload_screen.on_leave") as span:
        Logger.info(f"UploadScreen: Leaving {self.__class__.__name__}")
        self.clear_preview()
        self.selected_uri = None
        self.image_path = None
        self.parsed_menu_data = None
        self.is_ocr_mode = False
        self.set_status('')
        super().on_leave()