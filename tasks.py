from robocorp.tasks import task

from resources.steps import (start_environment, open_robot_order_website,
                             get_orders, close_annoying_modal,
                             fill_the_form, discard_any_alert_msg,
                             get_file_names, store_receipt_as_pdf,
                             screenshot_robot, embed_screenshot_to_receipt,
                             next_order, archive_receipts)


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """

    start_environment()
    open_robot_order_website()
    order_data = get_orders()
    for row in order_data:
        close_annoying_modal()
        fill_the_form(row)
        discard_any_alert_msg()
        pdf_file_name, png_file_name = get_file_names(row)
        store_receipt_as_pdf(pdf_file_name)
        screenshot_robot(png_file_name)
        embed_screenshot_to_receipt(png_file_name, pdf_file_name)
        next_order()
    archive_receipts()
