from io import BytesIO, StringIO

from csvalidate import ValidatedWriter
from flask import send_file


class CsvKit:

    @classmethod
    def send_csv(cls, iterable, filename, fields=None, schema=None, delimiter=',', encoding='utf-8', writer_kwargs=None,
                 **kwargs):
        buf = StringIO()

        # BOM (optional...Excel needs it to open UTF-8 file properly)
        buf.write('\ufeff')

        writer_cls = ValidatedWriter
        if schema:
            writer_cls = ValidatedWriter.from_schema(schema)
        writer_kwargs = writer_kwargs or {}
        writer = writer_cls(buf, fields, delimiter=delimiter, **writer_kwargs)
        writer.writeheader()
        for line in iterable:
            writer.writerow(line)
        buf.seek(0)
        buf = BytesIO(buf.read().encode(encoding))
        mimetype = 'Content-Type: text/csv; charset=' + encoding

        return send_file(buf, attachment_filename=filename, as_attachment=True, mimetype=mimetype, **kwargs)
