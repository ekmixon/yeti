from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

from core.investigation import ImportMethod


class ImportPDF(ImportMethod):

    default_values = {
        "name": "import_pdf",
        "description": "Perform investigation import from a PDF document.",
        "acts_on": "application/pdf",
    }

    def do_import(self, results, filepath):
        buff = StringIO()
        with open(filepath, "rb") as fp:
            laparams = LAParams()
            laparams.all_texts = True
            rsrcmgr = PDFResourceManager()
            pagenos = set()

            for page in PDFPage.get_pages(fp, pagenos, check_extractable=True):
                device = TextConverter(rsrcmgr, buff, codec="utf-8", laparams=laparams)
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                interpreter.process_page(page)

                buff.write("\n")

            results.investigation.update(import_text=buff.getvalue())

        buff.close()
