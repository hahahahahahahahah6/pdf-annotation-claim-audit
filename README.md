# Documentation claim auditor

This offline static auditor compares documented claims about the checked capability with Python source evidence. It never executes the inspected code.

## Usage

```sh
python3 -m pip install .
pdf-annotation-claim-audit audit . --json
python3 -m pdf_annotation_claim_audit audit . --verbose
```

The optional repository path defaults to the current directory. Use `--ignore PREFIX` repeatedly to exclude paths and `--fail-on medium` to include test-only evidence findings in the failure threshold. Exit status is 0 for PASS, 2 for findings at the selected threshold, and 1 for usage or I/O errors. Use `--version` to show the version.

The findings are:

```
documented-pdf-annotation-claim-false
documented-no-pdf-annotation-claim-false
```

## Differentiation

The checked operation adds interactive page objects. Extraction reads existing content; generation creates documents; merging and splitting rearrange pages; encryption, rotation, form filling, watermarking, redaction, compression and signing perform different operations.

## Limitations

This phrase can yield a false positive because a roadmap can mention a future feature:

```text
pdf annotation
```

This phrase can yield a false positive because a wrapper can lack an operation:

```text
annotate pdf
```

This phrase can yield a false positive because a code comment can be meant:

```text
add comment to pdf
```

This phrase can yield a false positive because a release note can be meant:

```text
add note to pdf
```

This phrase can yield a false positive because a viewer can highlight search hits:

```text
add highlight to pdf
```

This phrase can yield a false positive because an editor can apply syntax highlighting:

```text
highlight pdf
```

This phrase can yield a false positive because cropping or page numbering can be meant:

```text
annotate pdf page
```

This phrase can yield a false positive because a task tracker note can be meant:

```text
add sticky note to pdf
```

This phrase can yield a false positive because ordinary page text can be meant:

```text
add text annotation to pdf
```

This phrase can yield a false positive because form field text can be meant:

```text
add freetext to pdf
```

This phrase can yield a false positive because a workflow approval or watermark can be meant:

```text
add stamp to pdf
```

This phrase can yield a false positive because a reader-only tool can use the name:

```text
pdf annotator
```

- Pair routes are module-scoped, not variable-scoped: a PyMuPDF opener and an unrelated add_*_annot call in the same module count as evidence. The tool flags the claim; only the code decides.

- A PyMuPDF opener + add_*_annot call IS detected even if the annotated document is never saved: the call itself is the annotation fingerprint; the tool does not check whether the result is written out.

- A pypdf / PyPDF2 PdfWriter + add_annotation call IS detected even if the annotation dictionary was built by hand: the call itself is the annotation fingerprint; the tool does not check how the annotation was built.

- A generic annotation-named call IS detected even if it is called with no arguments: the name itself is the annotation fingerprint; the tool does not evaluate the arguments.

- A lone PyMuPDF opener call with no add_*_annot call is NOT detected: an opener that never annotates annotates nothing.

- A bare add_*_annot call is NOT detected unless a PyMuPDF opener call is present in the same module: the method name alone is too generic.

- A lone pypdf / PyPDF2 PdfWriter construction with no .add_annotation call is NOT detected: a writer that never attaches an annotation annotates nothing.

- A bare .add_annotation call is NOT detected unless a PdfWriter construction, an AnnotationBuilder call, or a pypdf annotation class construction is present in the same module: the method name alone is too generic.

- A lone AnnotationBuilder.* call is NOT detected: building an annotation dictionary without attaching it annotates nothing.

- A lone pypdf annotation class construction is NOT detected: building an annotation object without attaching it annotates nothing.

- A PyMuPDF opener + add_redact_annot call is NOT detected: adding a redaction annotation is the R242 family, not this one.

- A PyMuPDF opener + add_widget call is NOT detected: adding a form-field widget is the R240 form-filling family's domain, not this one.

- A PyMuPDF opener + set_rotation call is NOT detected: rotating a page or an annotation is the R239 family, not this one.

- A PyMuPDF opener + annots() / first_annot / load_annot reading alone is NOT detected: reading the annotations a PDF already has is the pdf-extraction family's domain, not this one.

- A pikepdf JobBuilder flatten_annotations call is NOT detected: flattening bakes existing annotations into page content — it removes annotations, the opposite direction.

- A reportlab Canvas drawing + save call alone is NOT detected: drawing shapes or text onto a page writes page content; it does not add an annotation.

- A PyMuPDF opener + insert_text / insert_textbox call alone is NOT detected: inserting text writes page content; it does not add an annotation.

- A PyMuPDF opener + draw_rect / draw_circle call alone is NOT detected: drawing a shape writes page content; it does not add an annotation.

- A pypdf / PyPDF2 PdfWriter + append / merge call is NOT detected: appending or merging whole files is the R236 merge route, not annotation.

- A pypdf / PyPDF2 PdfWriter + add_page call is NOT detected: adding pages is the R237 split route, not annotation.

- A pypdf / PyPDF2 PdfWriter + encrypt call is NOT detected: encrypting a PDF is the R238 family, not annotation.

- A pypdf / PyPDF2 PdfReader / PdfWriter + rotate call is NOT detected: rotating pages is the R239 family, not annotation.

- A pypdf / PyPDF2 PdfWriter + update_page_form_field_values call is NOT detected: filling a form is the R240 family, not annotation.

- A pypdf / PyPDF2 PdfReader + merge_page call is NOT detected: merging a page is the R241 watermarking route, not annotation.

- A PyMuPDF opener + show_pdf_page call is NOT detected: overlaying a page is the R241 watermarking route, not annotation.

- A PyMuPDF opener + rotated insert_text / insert_textbox call is NOT detected: inserting rotated text is the R241 watermarking route, not annotation.

- A pypdf / PyPDF2 PdfReader / PdfWriter + compress_content_streams call is NOT detected: compressing content streams is the R243 family, not annotation.

- A PyMuPDF opener + save call with a compression keyword is NOT detected: saving with compression knobs is the R243 family, not annotation.

- A pyhanko sign_pdf / endesive.pdf.cms.sign call is NOT detected: signing a PDF is the R231 e-signature family, not annotation.

- A pypdf / PyPDF2 PdfReader call is NOT detected: reading a PDF is not annotating it.

- PDF generation (reportlab Canvas + save, fpdf output, WeasyPrint write_pdf, openpyxl Workbook + save, and the rest of the pdf-generation family's routes) is NOT detected: writing one PDF from content is not annotating an existing PDF.

- PDF merging is NOT detected: combining two or more PDFs into one file is the R236 family, not this one.

- PDF splitting is NOT detected: splitting one PDF into separate files is the R237 family, not this one.

- PDF encryption is NOT detected: password-protecting a PDF is the R238 family, not this one.

- PDF rotation is NOT detected: rotating PDF pages is the R239 family, not this one.

- PDF form filling is NOT detected: entering data into AcroForm fields is the R240 family, not this one.

- PDF watermarking is NOT detected: stamping a watermark onto PDF pages is the R241 family, not this one.

- PDF redaction is NOT detected: removing text from PDF pages is the R242 family, not this one.

- PDF compression is NOT detected: shrinking a PDF is the R243 family, not this one.

- PDF extraction is NOT detected: reading text or field values out of a PDF is the pdf-extraction family, not this one.

- E-signature is NOT detected: applying a cryptographic signature to a PDF is the R231 family, not this one.

- qpdf / pdftk / Ghostscript subprocess calls are NOT detected: shelling out to an external binary is NOT evidence by design.

- Mindee parse with ANY product is NOT detected: mindee extracts fields from documents; it has no product for the checked operation.

- Azure begin_analyze_document with ANY model id is NOT detected: the call carries an opaque model id, not a typed call for the checked operation.

- Veryfi calls of ANY kind are NOT detected: veryfi extracts fields from documents; it has no method for the checked operation.

- Google Document AI process_document / batch_process_documents with ANY processor is NOT detected: the processor is named by an opaque per-project resource name, and Document AI has no operation for the checked feature.

- Eden AI universal-ai calls with ANY model id are NOT detected: Eden AI documents no model for the checked operation.

- Textract calls of ANY kind are NOT detected: Textract reads documents; it has no operation for the checked feature with a fixed fingerprint.

- LlamaParse calls are NOT detected: its parsing API reads documents; it has no operation for the checked feature.

- Nanonets / Docsumo / ABBYY Vantage / Rossum / Klippa / Parseur / Extend calls are NOT detected: opaque model / skill / queue / template / workflow IDs, or a generic upload endpoint with the document type configured outside the call — all extraction-side, no fixed fingerprint.

- A hand-rolled annotation built on raw PDF dictionary editing (appending to a page's /Annots list by hand with no listed call) is NOT detected: the tool requires a listed call.

- A detected annotation does not prove the annotation is visible or correct: the tool detects the annotation call, not the rendered result.

- Claims about extraction, generation, merging, splitting, encryption, rotation, forms, watermarking, redaction, compression, office documents, document extraction, image processing, signing, payments and OCR are outside the phrase lists.

- As with every family: static pattern matching, not semantic judgement; dead code counts; alias chains the tracer cannot follow are missed; exact phrases only, not semantics; denial handling depends on the denial phrase list; each route must sit in a single module.

