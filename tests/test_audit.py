import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from pdf_annotation_claim_audit.audit import audit, evidence
from pdf_annotation_claim_audit.phrases import PDFANNOTATION, NOPDFANNOTATION, GENERIC_NAMES
from pdf_annotation_claim_audit.__main__ import main

EXPECTED = (('annotate pdf', 'annotates pdf', 'annotating pdf', 'annotate pdfs', 'annotates pdfs', 'annotating pdfs', 'pdf annotation', 'pdf annotations', 'add annotation to pdf', 'adds annotation to pdf', 'adding annotation to pdf', 'add annotations to pdf', 'adds annotations to pdf', 'adding annotations to pdf', 'add comment to pdf', 'adds comment to pdf', 'adding comment to pdf', 'add note to pdf', 'adds note to pdf', 'adding note to pdf', 'add highlight to pdf', 'adds highlight to pdf', 'adding highlight to pdf', 'highlight pdf', 'highlights pdf', 'highlighting pdf', 'annotate pdf page', 'annotates pdf page', 'annotating pdf page', 'annotate pdf pages', 'annotates pdf pages', 'annotating pdf pages', 'add sticky note to pdf', 'adds sticky note to pdf', 'adding sticky note to pdf', 'add text annotation to pdf', 'adds text annotation to pdf', 'adding text annotation to pdf', 'add freetext to pdf', 'adds freetext to pdf', 'adding freetext to pdf', 'add stamp to pdf', 'adds stamp to pdf', 'adding stamp to pdf', 'pdf annotator', 'annotate pdf document', 'annotates pdf document', 'annotating pdf document', 'add pdf annotation', 'add pdf annotations'), ('no pdf annotation', 'does not annotate pdf', 'does not annotate pdfs', 'does not add annotation to pdf', 'does not add annotations to pdf', 'does not add comment to pdf', 'does not add note to pdf', 'does not add highlight to pdf', 'does not highlight pdf', 'does not annotate pdf page', 'does not annotate pdf pages', 'does not add sticky note to pdf', 'does not add text annotation to pdf', 'does not add freetext to pdf', 'does not add stamp to pdf', 'no pdf annotations', 'does not support pdf annotation', 'without pdf annotation', 'pdf annotation not supported', 'no pdf annotation support', 'pdf annotation not available', 'no pdf annotator', 'does not annotate pdf document', 'does not add pdf annotation'), ('annotate_pdf', 'annotate_pdfs', 'annotate_pdf_page', 'annotate_pdf_pages', 'annotate_pdf_document', 'add_annotation_to_pdf', 'add_annotations_to_pdf', 'add_pdf_annotation', 'add_pdf_annotations', 'add_comment_to_pdf', 'add_note_to_pdf', 'add_highlight_to_pdf', 'highlight_pdf', 'highlight_pdf_text', 'add_text_annotation_to_pdf', 'add_freetext_to_pdf', 'add_stamp_to_pdf', 'add_sticky_note_to_pdf', 'add_pdf_comment', 'add_pdf_note', 'pdf_annotate', 'pdf_add_annotation', 'add_annotation_to_pdf_page', 'add_pdf_highlight'))

class AuditTests(unittest.TestCase):
    def test_oracle(self):
        self.assertEqual((PDFANNOTATION, NOPDFANNOTATION, GENERIC_NAMES), EXPECTED)

    def test_routes(self):
        methods = ('text highlight underline strikeout squiggly freetext ink caret file line circle rect stamp polygon polyline').split()
        sources = ['import fitz; fitz.open(); page.add_%s_annot()' % m for m in methods]
        sources += ['from fitz import open as op; op(); p.add_text_annot()', 'import pymupdf; pymupdf.Document(); p.add_underline_annot()', 'import pymupdf; doc=pymupdf.open(); page=doc[0]; page.add_text_annot()']
        for lib in ('pypdf', 'PyPDF2'):
            sources += ['from %s import PdfWriter as W; W(); x.add_annotation()' % lib, 'import %s as p; p.PdfWriter(); x.add_annotation()' % lib]
        sources += ['from PyPDF2.generic import AnnotationBuilder as B; B.%s(); x.add_annotation()' % m for m in ('text','free_text','line','rectangle','link')]
        sources += ['from pypdf.annotations import %s as C; C(); x.add_annotation()' % c for c in ('Text','FreeText','Line','PolyLine','Rectangle','Highlight','Ellipse','Polygon','Link','Popup')]
        sources += ['import pypdf.annotations as a; a.Text(); x.add_annotation()', 'x.%s()' % 'annotate_pdf', 'from lib import annotate_pdf as a; a()']
        sources += ['x.%s()' % n for n in GENERIC_NAMES]
        for source in sources:
            with self.subTest(source=source): self.assertTrue(evidence(source))

    def test_non_routes(self):
        sources = ['import '+x for x in ('fitz','pymupdf','pypdf','PyPDF2','pikepdf','reportlab','pdfplumber')]
        sources += ['import fitz; fitz.open()', 'x.add_text_annot()', 'x.add_highlight_annot()', 'import pypdf; pypdf.PdfWriter()', 'x.add_annotation()', 'from PyPDF2.generic import AnnotationBuilder as B; B.text()', 'from pypdf.annotations import Text; Text()']
        sources += ['import fitz; fitz.open(); x.%s()' % n for n in ('add_redact_annot','add_widget','set_rotation','annots','load_annot','insert_text','insert_textbox','draw_rect','draw_circle','show_pdf_page','save','subset_fonts')]
        sources += ['import pypdf; pypdf.PdfWriter(); x.%s()' % n for n in ('append','merge','add_page','encrypt','update_page_form_field_values','compress_content_streams')]
        sources += ['import pypdf; pypdf.PdfReader(); x.%s()' % n for n in ('rotate','merge_page','compress_content_streams')]
        sources += ['pikepdf.JobBuilder().flatten_annotations()', 'reportlab.Canvas().save()', 'pdfplumber.open()', 'pdfminer.extract_text()', 'subprocess.run(["qpdf"])', 'subprocess.run(["gs"])', 'subprocess.run(["pdftk"])', 'mindee.parse(InvoiceV4)', 'azure.begin_analyze_document("prebuilt-read")', 'veryfi.Client()', 'documentai.process_document()', 'textract.analyze_document()', 'eden.universal_ai()', 'llamaparse.parse()', 'nanonets.ocr(model_id=opaque)', 'docsumo.upload()', 'pyhanko.sign_pdf()', 'def annotate_pdf(): pass\nx.annotate_pdf()', 'import fitz\nwith obj as fitz: pass\nfitz.open(); x.add_text_annot()', 'annotate_pdf()', 'invalid syntax !!!']
        for source in sources:
            with self.subTest(source=source): self.assertFalse(evidence(source))

    def test_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); doc=root/'README.md'; src=root/'app.py'
            doc.write_text('annotate pdf'); result=audit(root); self.assertEqual(result['findings'][0]['rule'], 'documented-pdf-annotation-claim-false'); self.assertEqual(result['findings'][0]['severity'], 'HIGH')
            src.write_text('x.annotate_pdf()'); self.assertEqual(audit(root)['verdict'], 'PASS')
            doc.write_text('does not annotate pdf'); self.assertEqual(audit(root)['findings'][0]['rule'], 'documented-no-pdf-annotation-claim-false')
            src.unlink(); self.assertEqual(audit(root)['verdict'], 'PASS')
            doc.write_text('```\nannotate pdf\n```'); self.assertEqual(audit(root)['verdict'], 'PASS')
            doc.write_text('`annotate pdf`'); self.assertEqual(audit(root)['verdict'], 'FAIL')
            (root/'tests').mkdir(); (root/'tests'/'test_x.py').write_text('x.annotate_pdf()')
            self.assertEqual(audit(root)['findings'][0]['severity'], 'MEDIUM'); self.assertEqual(audit(root)['verdict'], 'PASS'); self.assertEqual(audit(root, fail_on='medium')['verdict'], 'FAIL')
            doc.write_text('Nothing claimed'); self.assertEqual(audit(root)['verdict'], 'PASS')

    def test_split_symlink_ignore(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'README.md').write_text('annotate pdf'); (root/'a.py').write_text('import fitz; fitz.open()'); (root/'b.py').write_text('x.add_text_annot()')
            self.assertEqual(audit(root)['verdict'], 'FAIL')
            (root/'b.py').write_text('x.annotate_pdf()'); (root/'link.py').symlink_to(root/'b.py'); self.assertEqual(audit(root, ignore=['b.py'])['verdict'], 'FAIL')

    def test_cli(self):
        v=subprocess.run([sys.executable, '-m', 'pdf_annotation_claim_audit', '--version'], capture_output=True, text=True); self.assertEqual(v.stdout.strip(), '0.1.0')
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp,'README.md').write_text('annotate pdf')
            p=subprocess.run([sys.executable,'-m','pdf_annotation_claim_audit','audit',tmp,'--json'], capture_output=True, text=True)
            self.assertEqual(p.returncode,2); self.assertEqual(json.loads(p.stdout)['verdict'],'FAIL'); self.assertTrue(json.loads(p.stdout)['findings'][0]['message']); self.assertEqual(main(['audit',tmp]),2)
            Path(tmp,'tests').mkdir(); Path(tmp,'tests','test_x.py').write_text('x.annotate_pdf()')
            self.assertEqual(main(['audit',tmp]),0); self.assertEqual(main(['audit',tmp,'--fail-on','medium']),2)

if __name__ == '__main__': unittest.main()
