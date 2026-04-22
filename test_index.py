import sys
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: errors.append(str(err)))
        
        # Load the index.html via file protocol
        print("Loading index.html...")
        page.goto("file:///c:/Users/santi/Documents/Santiago/CD/proyectos/importaciones%20Bogota/index.html")
        page.wait_for_timeout(2000)
        
        # We can also test via http output
        print("Errors found:")
        for err in errors:
            print(" -", err)
            
        browser.close()

if __name__ == "__main__":
    main()
