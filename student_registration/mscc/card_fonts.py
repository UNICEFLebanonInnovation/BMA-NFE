"""Keep the examination card's Arabic type portable in its Word document."""

from pathlib import Path
from uuid import uuid4


ARABIC_CARD_FONT = 'Noto Naskh Arabic'


def embed_arabic_card_font(document):
    """Embed the licensed bold Naskh face, including glyphs needed for edits.

    Word's font part obfuscates only the first 32 bytes using the reversed
    font-key bytes. This is the Office document format, not encryption.
    """
    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    from docx.opc.oxml import serialize_part_xml
    from docx.opc.packuri import PackURI
    from docx.opc.part import Part
    from docx.oxml import OxmlElement, parse_xml
    from docx.oxml.ns import qn

    font_bytes = Path(__file__).with_name('fonts').joinpath('NotoNaskhArabic-Bold.ttf').read_bytes()
    font_key = uuid4()
    key_bytes = font_key.bytes[::-1]
    obfuscated = bytes(value ^ key_bytes[index % 16] for index, value in enumerate(font_bytes[:32]))
    font_part = Part(
        PackURI('/word/fonts/NotoNaskhArabic-Bold.odttf'),
        'application/vnd.openxmlformats-officedocument.obfuscatedFont',
        obfuscated + font_bytes[32:], document.part.package,
    )
    font_table = document.part.part_related_by(RT.FONT_TABLE)
    relationship_id = font_table.relate_to(font_part, RT.FONT)
    root = parse_xml(font_table.blob)
    font = OxmlElement('w:font')
    font.set(qn('w:name'), ARABIC_CARD_FONT)
    embedded = OxmlElement('w:embedBold')
    embedded.set(qn('r:id'), relationship_id)
    embedded.set(qn('w:fontKey'), '{' + str(font_key).upper() + '}')
    embedded.set(qn('w:subsetted'), '0')
    font.append(embedded)
    root.append(font)
    # python-docx exposes its default font table as a generic binary Part.
    font_table._blob = serialize_part_xml(root)

    settings = document.settings.element
    for tag in ('w:embedTrueTypeFonts', 'w:saveSubsetFonts'):
        existing = settings.find(qn(tag))
        if existing is not None:
            settings.remove(existing)
    # These follow the print settings in Word's ordered settings schema.
    print_settings = {
        qn('w:' + tag) for tag in (
            'writeProtection', 'view', 'zoom', 'removePersonalInformation',
            'removeDateAndTime', 'doNotDisplayPageBoundaries',
            'displayBackgroundShape', 'printPostScriptOverText',
            'printFractionalCharacterWidth', 'printFormsData',
        )
    }
    insertion_index = next(
        (index for index, child in enumerate(settings) if child.tag not in print_settings),
        len(settings),
    )
    settings.insert(insertion_index, OxmlElement('w:embedTrueTypeFonts'))
