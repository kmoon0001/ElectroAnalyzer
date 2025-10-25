"""Test data creation utilities for document processing tests.

This module provides functions to create various types of test documents
for comprehensive testing of document processing capabilities.
"""

import io
import tempfile
from pathlib import Path
from typing import Optional
import zipfile
from PIL import Image
import numpy as np


def create_test_pdf(content: str, with_images: bool = False) -> bytes:
    """Create a test PDF file with the given content.

    Args:
        content: Text content to include in the PDF
        with_images: Whether to include test images

    Returns:
        PDF file content as bytes
    """
    # Simple PDF structure for testing
    pdf_content = f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length {len(content) + 20}
>>
stream
BT
/F1 12 Tf
72 720 Td
({content}) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000200 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
{300 + len(content)}
%%EOF"""

    return pdf_content.encode()


def create_test_docx(content: str) -> bytes:
    """Create a test DOCX file with the given content.

    Args:
        content: Text content to include in the DOCX

    Returns:
        DOCX file content as bytes
    """
    # Create a simple DOCX structure
    docx_buffer = io.BytesIO()

    with zipfile.ZipFile(docx_buffer, 'w') as docx_zip:
        # Add document.xml
        document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p>
            <w:r>
                <w:t>{content}</w:t>
            </w:r>
        </w:p>
    </w:body>
</w:document>"""

        docx_zip.writestr('word/document.xml', document_xml)

        # Add minimal required files
        docx_zip.writestr('[Content_Types].xml', """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")

        docx_zip.writestr('_rels/.rels', """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""")

        docx_zip.writestr('word/_rels/document.xml.rels', """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>""")

    docx_buffer.seek(0)
    return docx_buffer.getvalue()


def create_test_image(content: str, width: int = 200, height: int = 100) -> bytes:
    """Create a test image file with the given content.

    Args:
        content: Text content to include in the image
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Image file content as bytes
    """
    # Create a simple image with text
    image = Image.new('RGB', (width, height), color='white')

    # For testing purposes, we'll create a simple colored image
    # In a real scenario, you might use PIL's ImageDraw to add text
    image_array = np.array(image)

    # Add some pattern to make it more realistic
    for i in range(height):
        for j in range(width):
            if (i + j) % 10 == 0:
                image_array[i, j] = [200, 200, 200]  # Light gray pattern

    image = Image.fromarray(image_array)

    # Save to bytes
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    return img_buffer.getvalue()


def create_test_txt(content: str) -> bytes:
    """Create a test text file with the given content.

    Args:
        content: Text content to include in the file

    Returns:
        Text file content as bytes
    """
    return content.encode('utf-8')


def create_malicious_file(content_type: str = "script") -> bytes:
    """Create a malicious file for security testing.

    Args:
        content_type: Type of malicious content to create

    Returns:
        Malicious file content as bytes
    """
    if content_type == "script":
        return b"<script>alert('XSS')</script>"
    elif content_type == "javascript":
        return b"javascript:alert('XSS')"
    elif content_type == "iframe":
        return b"<iframe src='javascript:alert(\"XSS\")'></iframe>"
    elif content_type == "object":
        return b"<object data='javascript:alert(\"XSS\")'></object>"
    elif content_type == "embed":
        return b"<embed src='javascript:alert(\"XSS\")'></embed>"
    elif content_type == "link":
        return b"<link rel='stylesheet' href='javascript:alert(\"XSS\")'>"
    elif content_type == "meta":
        return b"<meta http-equiv='refresh' content='0;url=javascript:alert(\"XSS\")'>"
    elif content_type == "style":
        return b"<style>body{background:url('javascript:alert(\"XSS\")')}</style>"
    elif content_type == "expression":
        return b"<style>body{background:expression(alert('XSS'))}</style>"
    elif content_type == "import":
        return b"@import url('javascript:alert(\"XSS\")');"
    elif content_type == "data_html":
        return b"data:text/html,<script>alert('XSS')</script>"
    elif content_type == "data_js":
        return b"data:application/javascript,alert('XSS')"
    elif content_type == "blob":
        return b"blob:javascript:alert('XSS')"
    elif content_type == "file":
        return b"file:///etc/passwd"
    elif content_type == "ftp":
        return b"ftp://malicious.com/file"
    elif content_type == "gopher":
        return b"gopher://malicious.com/"
    elif content_type == "jar":
        return b"jar:file:///malicious.jar!/"
    elif content_type == "ldap":
        return b"ldap://malicious.com/"
    elif content_type == "mailto":
        return b"mailto:malicious@evil.com"
    elif content_type == "tel":
        return b"tel:+1234567890"
    elif content_type == "telnet":
        return b"telnet://malicious.com/"
    elif content_type == "ws":
        return b"ws://malicious.com/"
    elif content_type == "wss":
        return b"wss://malicious.com/"
    else:
        return b"Unknown malicious content type"


def create_oversized_file(size_mb: int = 51) -> bytes:
    """Create an oversized file for testing file size limits.

    Args:
        size_mb: Size of the file in megabytes

    Returns:
        Oversized file content as bytes
    """
    # Create content that's larger than the allowed limit
    content_size = size_mb * 1024 * 1024  # Convert MB to bytes
    return b"x" * content_size


def create_corrupted_file(file_type: str = "pdf") -> bytes:
    """Create a corrupted file for testing error handling.

    Args:
        file_type: Type of file to corrupt

    Returns:
        Corrupted file content as bytes
    """
    if file_type == "pdf":
        return b"Corrupted PDF content that will cause parsing errors"
    elif file_type == "docx":
        return b"Corrupted DOCX content that will cause parsing errors"
    elif file_type == "image":
        return b"Corrupted image content that will cause parsing errors"
    elif file_type == "txt":
        return b"Corrupted text content that will cause parsing errors"
    else:
        return b"Corrupted file content that will cause parsing errors"


def create_file_with_special_characters() -> bytes:
    """Create a file with special characters for testing encoding handling.

    Returns:
        File content with special characters as bytes
    """
    special_chars = """
    Special characters test:
    - Latin: àáâãäåæçèéêë
    - Cyrillic: абвгдеёжзийклмнопрстуфхцчшщъыьэюя
    - Greek: αβγδεζηθικλμνξοπρστυφχψω
    - Arabic: العربية
    - Chinese: 中文
    - Japanese: 日本語
    - Korean: 한국어
    - Thai: ไทย
    - Hebrew: עברית
    - Devanagari: हिन्दी
    - Symbols: !@#$%^&*()_+-=[]{}|;':\",./<>?
    - Emoji: 😀😁😂🤣😃😄😅😆😉😊😋😎😍😘🥰😗😙😚☺️🙂🤗🤩🤔🤨😐😑😶🙄😏😣😥😮🤐😯😪😫😴😌😛😜😝🤤😒😓😔😕🙃🤑😲☹️🙁😖😞😟😤😢😭😦😧😨😩🤯😬😰😱🥵🥶😳🤪😵😡😠🤬😷🤒🤕🤢🤮🤧🥴😇🤠🤡🥳🥺🤥🤫🤭🧐🤓😈👿👹👺💀👻👽👾🤖💩😺😸😹😻😼😽🙀😿😾
    """

    return special_chars.encode('utf-8')


def create_file_with_unicode_content() -> bytes:
    """Create a file with Unicode content for testing Unicode handling.

    Returns:
        File content with Unicode characters as bytes
    """
    unicode_content = """
    Unicode content test:

    Basic Latin: ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz
    Latin-1 Supplement: ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞß àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ
    Latin Extended-A: ĀĂĄĆĈĊČĎĐĒĔĖĘĚĜĞĠĢĤĦĨĪĬĮİĲĴĶĹĻĽĿŁŃŅŇŊŌŎŐŒŔŖŘŚŜŞŠŢŤŦŨŪŬŮŰŲŴŶŸŹŻŽ
    Latin Extended-B: ƀƁƂƃƄƅƆƇƈƉƊƋƌƍƎƏƐƑƒƓƔƕƖƗƘƙƚƛƜƝƞƟƠơƢƣƤƥƦƧƨƩƪƫƬƭƮƯưƱƲƳƴƵƶƷƸƹƺƻƼƽƾƿ
    Cyrillic: АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ абвгдеёжзийклмнопрстуфхцчшщъыьэюя
    Greek: ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ αβγδεζηθικλμνξοπρστυφχψω
    Arabic: العربية
    Hebrew: עברית
    Devanagari: हिन्दी
    Chinese: 中文
    Japanese: 日本語
    Korean: 한국어
    Thai: ไทย
    """

    return unicode_content.encode('utf-8')


def create_file_with_mixed_encodings() -> bytes:
    """Create a file with mixed encodings for testing encoding detection.

    Returns:
        File content with mixed encodings as bytes
    """
    mixed_content = """
    Mixed encoding test:

    ASCII: Hello World!
    Latin-1: Café résumé naïve
    UTF-8: 中文 العربية русский
    Mixed: Hello 世界 مرحبا мир
    """

    return mixed_content.encode('utf-8')


def create_file_with_empty_lines() -> bytes:
    """Create a file with empty lines for testing line handling.

    Returns:
        File content with empty lines as bytes
    """
    content_with_empty_lines = """
    Line 1


    Line 2

    Line 3


    Line 4
    """

    return content_with_empty_lines.encode('utf-8')


def create_file_with_very_long_lines() -> bytes:
    """Create a file with very long lines for testing line length handling.

    Returns:
        File content with very long lines as bytes
    """
    long_line = "A" * 10000
    return long_line.encode()


def create_file_with_binary_content() -> bytes:
    """Create a file with binary content for testing binary handling.

    Returns:
        File content with binary data as bytes
    """
    # Create binary content with various byte values
    binary_content = bytes(range(256))  # All possible byte values
    return binary_content


def create_nested_directory_structure(base_path: Path, depth: int = 3) -> Path:
    """Create a nested directory structure for testing path handling.

    Args:
        base_path: Base path for the directory structure
        depth: Depth of nesting

    Returns:
        Path to the deepest directory
    """
    current_path = base_path

    for i in range(depth):
        current_path = current_path / f"level{i+1}"
        current_path.mkdir(exist_ok=True)

    return current_path


def create_file_with_permission_issues(file_path: Path) -> None:
    """Create a file with permission issues for testing permission handling.

    Args:
        file_path: Path to the file to create
    """
    file_path.write_text("Content with permission issues")
    # Note: Permission changes would be handled in the test, not here


def create_file_with_concurrent_access(file_path: Path, content: str) -> None:
    """Create a file for concurrent access testing.

    Args:
        file_path: Path to the file to create
        content: Content to write to the file
    """
    file_path.write_text(content)
