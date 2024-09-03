import os
import shutil

from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
# from PIL import Image

from config.filelocation import (WEBSITE_URL, INPUT_CSV_FILE, LOCAL_CSV_FILE,
                                 LOCAL_ORDER_PDF_FILE, LOCAL_ROBOT_PNG_FILE,
                                 LOCAL_DIR_FOR_ORDER_PDF_FILE,
                                 LOCAL_DIR_FOR_ROBOT_PNG_FILE,
                                 LOCAL_ZIP_FILE)
from resources.types import RobotOrderData


page = None


def clean_output_directory(dir_to_clean: str) -> None:
    """Removing previous pdf-orders"""
    if os.path.isdir(dir_to_clean):
        shutil.rmtree(dir_to_clean)
    os.makedirs(dir_to_clean)


def start_environment() -> None:
    """Configure environment to run automation."""
    browser.configure(
        slowmo=100   # milliseconds
    )
    clean_output_directory(LOCAL_DIR_FOR_ORDER_PDF_FILE)
    clean_output_directory(LOCAL_DIR_FOR_ROBOT_PNG_FILE)


def open_robot_order_website(site: str = WEBSITE_URL) -> None:
    """Navigates to the given url site."""
    global page
    browser.goto(site)
    page = browser.page()


def get_orders(csv_file: str = INPUT_CSV_FILE,
               local_csv_file: str = LOCAL_CSV_FILE) -> Tables:
    """Download the orders file, read it as a table, and return the result."""

    # Download the file
    http = HTTP()
    http.download(url=csv_file, target_file=local_csv_file, overwrite=True)

    # Read it as a table
    library = Tables()
    order_data = library.read_table_from_csv(local_csv_file)
    return order_data


def close_annoying_modal() -> None:
    """Get rid of annoying modal pops up when you open the website."""
    page.locator("button:text('OK')").click()


def fill_the_form(robot_order: RobotOrderData) -> None:
    """Insert the robot order and save each order HTML receipt as a PDF file"""
    body_locator = f"#id-body-{robot_order['Body']}"
    leg_input_locator = "xpath=//label[contains(.,'3. Legs:')]/../input"

    page.locator("#head").select_option(str(robot_order["Head"]))
    page.locator(body_locator).click()
    page.locator(leg_input_locator).fill(robot_order["Legs"])
    page.locator("#address").fill(robot_order["Address"])
    page.locator("#preview").click()
    page.locator("#order").click()


def discard_any_alert_msg() -> None:
    alert_msg_locator = 'div.alert.alert-danger'
    while page.locator(alert_msg_locator).is_visible():
        page.locator("#order").click()


def get_file_names(robot_order: RobotOrderData) -> None:
    pdf_file_name = LOCAL_ORDER_PDF_FILE.format(robot_order["Order number"])
    png_file_name = LOCAL_ROBOT_PNG_FILE.format(robot_order["Order number"])
    return pdf_file_name, png_file_name


def store_receipt_as_pdf(local_order_pdf) -> None:
    """Export the order receipt to a pdf file."""
    robot_receipt_order = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(robot_receipt_order, local_order_pdf)


def screenshot_robot(local_robot_png) -> None:
    """Take a screenshot of of the ordered robot."""
    robot_image = page.locator("#robot-preview-image")
    image_bytes = browser.screenshot(robot_image)
    with open(local_robot_png, "wb") as file:
        file.write(image_bytes)


# def resize_image(local_robot_png, scale_factor=0.5):
#     """Resize the image to the specified scale factor."""
#     with Image.open(local_robot_png) as img:
#         width, height = img.size
#         new_width = int(width * scale_factor)
#         new_height = int(height * scale_factor)
#         img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
#         img.save('output/png-robots/temp.png')


def embed_screenshot_to_receipt(png_file, pdf_file):
    """Embed the robot screenshot to the order PDF file"""
    file_to_add = f'{png_file}:align=center'
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[file_to_add],
        target_document=pdf_file,
        append=True
    )


def next_order() -> None:
    """Request to create another robot order."""
    page.locator("#order-another").click()


def archive_receipts(pdf_folder: str = LOCAL_DIR_FOR_ORDER_PDF_FILE,
                     zip_file: str = LOCAL_ZIP_FILE) -> None:
    """Create a ZIP file of receipt PDF files."""
    lib = Archive()
    lib.archive_folder_with_zip(pdf_folder, zip_file)
