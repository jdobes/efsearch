from frontend.html_writer import HTMLWriter


class PageSearch:
    def __init__(self):
        self.writer = HTMLWriter()
    def getHTML(self):
        return self.writer.get_header() + self.writer.get_content() + self.writer.get_footer()
