import os
import re
from bs4 import BeautifulSoup

# Configuration
ROOT_DIR = "."
REVIEWS_DIR = "nuclear_biology_reviews/reviews"

# Templates
HEADER_TEMPLATE = """
    <header class="bg-white shadow-sm border-b">
        <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <!-- Logo/Branding -->
                <div class="flex items-center">
                    <div class="flex-shrink-0 flex items-center">
                        <a href="{root_path}/index.html" class="flex items-center">
                            <i class="fas fa-atom text-blue-600 text-2xl mr-3"></i>
                            <span class="text-xl font-bold text-gray-900">CellNucleus.com</span>
                        </a>
                    </div>
                </div>

                <!-- Navigation Menu -->
                <div class="hidden md:block">
                    <div class="ml-10 flex items-baseline space-x-8">
                        <a href="{root_path}/index.html" class="text-blue-600 hover:text-blue-800 px-3 py-2 rounded-md text-sm font-medium">Home</a>
                        <a href="{root_path}/reviews_index.html" class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">All Reviews</a>
                        <a href="{root_path}/index.html#reviews" class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">Categories</a>
                        <a href="{root_path}/index.html#microscopy" class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">Microscopy</a>
                        <a href="{root_path}/index.html#structure" class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">Structure</a>
                        <a href="{root_path}/downloads.html" class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">Downloads</a>
                        <a href="{root_path}/index.html#about" class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">About</a>
                    </div>
                </div>

                <!-- Mobile Menu Button -->
                 <div class="-mr-2 flex md:hidden">
                    <button type="button" id="mobile-menu-btn" class="bg-white inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500" aria-controls="mobile-menu" aria-expanded="false">
                        <span class="sr-only">Open main menu</span>
                        <i class="fas fa-bars"></i>
                    </button>
                </div>
            </div>
            <!-- Mobile Menu (Hidden by default) -->
            <div class="hidden md:hidden" id="mobile-menu">
                <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
                    <a href="{root_path}/index.html" class="text-gray-700 hover:text-blue-600 block px-3 py-2 rounded-md text-base font-medium">Home</a>
                    <a href="{root_path}/reviews_index.html" class="text-gray-700 hover:text-blue-600 block px-3 py-2 rounded-md text-base font-medium">All Reviews</a>
                    <a href="{root_path}/index.html#reviews" class="text-gray-700 hover:text-blue-600 block px-3 py-2 rounded-md text-base font-medium">Categories</a>
                    <a href="{root_path}/index.html#microscopy" class="text-gray-700 hover:text-blue-600 block px-3 py-2 rounded-md text-base font-medium">Microscopy</a>
                    <a href="{root_path}/index.html#structure" class="text-gray-700 hover:text-blue-600 block px-3 py-2 rounded-md text-base font-medium">Structure</a>
                    <a href="{root_path}/downloads.html" class="text-gray-700 hover:text-blue-600 block px-3 py-2 rounded-md text-base font-medium">Downloads</a>
                    <a href="{root_path}/index.html#about" class="text-gray-700 hover:text-blue-600 block px-3 py-2 rounded-md text-base font-medium">About</a>
                </div>
            </div>
        </nav>
    </header>
"""

FOOTER_TEMPLATE = """
    <footer class="bg-gray-900 text-white py-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div>
                    <div class="flex items-center mb-4">
                        <i class="fas fa-atom text-blue-400 text-2xl mr-3"></i>
                        <span class="text-xl font-bold">CellNucleus.com</span>
                    </div>
                    <p class="text-gray-300">Comprehensive nuclear biology research platform providing access to cutting-edge reviews and educational resources.</p>
                </div>
                <div>
                    <h4 class="text-lg font-semibold mb-4">Quick Links</h4>
                    <ul class="space-y-2 text-gray-300">
                        <li><a href="{root_path}/index.html#reviews" class="hover:text-white">Research Reviews</a></li>
                        <li><a href="{root_path}/index.html#microscopy" class="hover:text-white">Microscopy</a></li>
                        <li><a href="{root_path}/downloads.html" class="hover:text-white">Downloads</a></li>
                        <li><a href="{root_path}/index.html#about" class="hover:text-white">About</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="text-lg font-semibold mb-4">Contact & Share</h4>
                    <div class="space-y-2 text-gray-300">
                        <div><i class="fas fa-envelope mr-2"></i> mhendzel@ualberta.ca</div>
                        <div><i class="fas fa-globe mr-2"></i> www.cellnucleus.com</div>
                    </div>
                </div>
            </div>
            <div class="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
                <p>&copy; 2025 CellNucleus.com - Nuclear Biology Research Hub.</p>
            </div>
        </div>
    </footer>
"""

SCRIPT_TEMPLATE = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const mobileMenuBtn = document.getElementById('mobile-menu-btn');
            const mobileMenu = document.getElementById('mobile-menu');

            if (mobileMenuBtn && mobileMenu) {
                mobileMenuBtn.addEventListener('click', function() {
                    mobileMenu.classList.toggle('hidden');
                    const expanded = mobileMenuBtn.getAttribute('aria-expanded') === 'true' || false;
                    mobileMenuBtn.setAttribute('aria-expanded', !expanded);
                });
            }
        });
    </script>
"""

def get_title_from_filename(filename):
    name = os.path.splitext(filename)[0]
    # Remove suffixes like -review, -comprehensive-review
    name = re.sub(r'-comprehensive-review$', '', name)
    name = re.sub(r'-review$', '', name)
    name = re.sub(r'-critical-review$', '', name)
    # Replace dashes with spaces and title case
    return name.replace('-', ' ').title()

def clean_genspark(soup):
    # Remove scripts with 'genspark' in content or src or id
    for script in soup.find_all('script'):
        if script.get('src') and 'genspark' in script.get('src'):
            script.decompose()
        elif script.string and 'genspark' in script.string:
            script.decompose()
        elif script.get('id') and 'genspark' in script.get('id'):
            script.decompose()
    return soup

def update_file(filepath, is_root=False):
    print(f"Updating {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    soup = BeautifulSoup(content, 'html.parser')

    # Remove Genspark artifacts
    soup = clean_genspark(soup)

    root_path = "." if is_root else "../.."

    # Prepare new header and footer
    new_header_html = HEADER_TEMPLATE.format(root_path=root_path)
    new_footer_html = FOOTER_TEMPLATE.format(root_path=root_path)
    new_script_html = SCRIPT_TEMPLATE

    new_header_soup = BeautifulSoup(new_header_html, 'html.parser')
    new_footer_soup = BeautifulSoup(new_footer_html, 'html.parser')
    new_script_soup = BeautifulSoup(new_script_html, 'html.parser')

    # Replace Header
    header = soup.find('header')
    if header:
        header.replace_with(new_header_soup)
    else:
        if soup.body:
            soup.body.insert(0, new_header_soup)

    # Replace Footer
    footer = soup.find('footer')
    if footer:
        footer.replace_with(new_footer_soup)
    else:
        if soup.body:
            soup.body.append(new_footer_soup)

    # Add Script
    # Check if script already exists (to avoid duplicates if re-running)
    # Simple check: see if we can find the mobile-menu-btn logic
    existing_script = False
    for script in soup.find_all('script'):
        if script.string and 'mobile-menu-btn' in script.string:
            existing_script = True
            break

    if not existing_script:
        if soup.body:
            soup.body.append(new_script_soup)

    # For Review pages: Fix Title if it's the generic "Nuclear Bodies" one but filename says otherwise
    if not is_root:
        title_tag = soup.find('title')
        filename = os.path.basename(filepath)
        derived_title = get_title_from_filename(filename)

        if title_tag:
            current_title = title_tag.string.strip()
            if "Nuclear Bodies: Architecture and Function" in current_title and "nuclear-bodies" not in filename:
                print(f"  Fixing title: {current_title} -> {derived_title} | Nuclear Biology Reviews")
                title_tag.string = f"{derived_title} | Nuclear Biology Reviews"

            # Also check H1
            h1 = soup.find('h1')
            if h1 and "Nuclear Bodies: Architecture and Function" in h1.get_text() and "nuclear-bodies" not in filename:
                 h1.string = derived_title

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

def main():
    # 1. Update Category Pages (Root)
    for filename in os.listdir(ROOT_DIR):
        if filename.endswith('_category.html') or filename == 'reviews_index.html' or filename == 'index.html':
            update_file(os.path.join(ROOT_DIR, filename), is_root=True)

    # 2. Update Review Pages (Nested)
    if os.path.exists(REVIEWS_DIR):
        for filename in os.listdir(REVIEWS_DIR):
            if filename.endswith('.html'):
                update_file(os.path.join(REVIEWS_DIR, filename), is_root=False)

if __name__ == "__main__":
    main()
