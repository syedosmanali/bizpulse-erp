import os
import glob

# Emoji to Lucide icon mapping
emoji_to_lucide = {
    # Page headers
    '📦': '<i data-lucide="package"></i>',
    '🏢': '<i data-lucide="building-2"></i>',
    '🏦': '<i data-lucide="landmark"></i>',
    '📄': '<i data-lucide="file-text"></i>',
    '🚚': '<i data-lucide="truck"></i>',
    '🛒': '<i data-lucide="shopping-cart"></i>',
    '📋': '<i data-lucide="clipboard-list"></i>',
    '✅': '<i data-lucide="package-check"></i>',
    '📅': '<i data-lucide="calendar-clock"></i>',
    '🔍': '<i data-lucide="scan-barcode"></i>',
    '👥': '<i data-lucide="users"></i>',
    '🏪': '<i data-lucide="store"></i>',
    '💼': '<i data-lucide="users-round"></i>',
    '💳': '<i data-lucide="credit-card"></i>',
    '📈': '<i data-lucide="trending-up"></i>',
    '📊': '<i data-lucide="bar-chart-3"></i>',
    '⚙️': '<i data-lucide="settings"></i>',
    
    # Action buttons
    '➕': '<i data-lucide="plus"></i>',
    '✏️': '<i data-lucide="edit-2"></i>',
    '🗑️': '<i data-lucide="trash-2"></i>',
    '💾': '<i data-lucide="save"></i>',
    '❌': '<i data-lucide="x"></i>',
    '📥': '<i data-lucide="download"></i>',
    '📤': '<i data-lucide="upload"></i>',
    '🖨️': '<i data-lucide="printer"></i>',
    '📧': '<i data-lucide="mail"></i>',
    '💬': '<i data-lucide="message-circle"></i>',
    '🔄': '<i data-lucide="refresh-cw"></i>',
    '⬅️': '<i data-lucide="arrow-left"></i>',
    '➡️': '<i data-lucide="arrow-right"></i>',
    '✓': '<i data-lucide="check"></i>',
    'ℹ️': '<i data-lucide="info"></i>',
    '⚠️': '<i data-lucide="alert-triangle"></i>',
    
    # Status icons
    '✔️': '<i data-lucide="check-circle"></i>',
    '❎': '<i data-lucide="x-circle"></i>',
    '⏳': '<i data-lucide="clock"></i>',
    
    # Additional common emojis
    '+': '<i data-lucide="plus"></i>',  # Plain plus sign in buttons
}


def replace_emojis_in_file(filepath, emoji_map):
    """Replace all emojis in a file with Lucide icons."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for emoji, lucide_icon in emoji_map.items():
        content = content.replace(emoji, lucide_icon)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """Main function to process all ERP HTML files."""
    template_dir = 'frontend/screens/templates'
    erp_files = glob.glob(os.path.join(template_dir, 'erp_*.html'))
    
    print(f"Found {len(erp_files)} ERP HTML files")
    print("Replacing emojis with Lucide icons...\n")
    
    updated_count = 0
    for filepath in erp_files:
        filename = os.path.basename(filepath)
        if replace_emojis_in_file(filepath, emoji_to_lucide):
            print(f"✓ Updated: {filename}")
            updated_count += 1
        else:
            print(f"- No changes: {filename}")
    
    print(f"\n✅ Complete! Updated {updated_count}/{len(erp_files)} files")


if __name__ == '__main__':
    main()
