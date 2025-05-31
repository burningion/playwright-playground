import asyncio
from playwright.async_api import async_playwright
import logging
import click
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def click_all_links(url, headless=False):
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=headless)  # Use the headless parameter
        context = await browser.new_context(record_video_dir='videos', record_video_size={'width': 1280, 'height': 720})
        page = await context.new_page()
        
        try:
            # Navigate to the website
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until="networkidle")
            
            # Wait for page to fully load
            await page.wait_for_timeout(2000)
            
            # Find all links on the page
            links = await page.query_selector_all('a[href]')
            logger.info(f"Found {len(links)} links on the page")
            
            # Get link information before clicking and deduplicate
            link_info = []
            seen_urls = set()
            
            for link in links:
                href = await link.get_attribute('href')
                text = await link.inner_text()
                
                # Skip empty links or javascript links
                if href and not href.startswith('javascript:') and not href.startswith('#'):
                    # Convert relative URLs to absolute URLs for proper deduplication
                    parsed_base = urlparse(url)
                    base_url = f"{parsed_base.scheme}://{parsed_base.netloc}"
                    
                    if href.startswith('/'):
                        full_url = f"{base_url}{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = f"{base_url}/{href}"
                    
                    # Only add if we haven't seen this URL before
                    if full_url not in seen_urls:
                        seen_urls.add(full_url)
                        link_info.append({
                            'href': href,  # Keep original href for selector
                            'full_url': full_url,  # Store full URL for logging
                            'text': text.strip()[:50] if text else 'No text'  # Limit text length
                        })
            
            logger.info(f"Will click on {len(link_info)} unique links (deduplicated from {len(links)} total links)")
            
            # Click on each link one by one
            for i, info in enumerate(link_info, 1):
                try:
                    logger.info(f"Clicking link {i}/{len(link_info)}: {info['text']} -> {info['full_url']}")
                    
                    # Find the link element again (in case page has changed)
                    link_selector = f'a[href="{info["href"]}"]'
                    link_element = await page.query_selector(link_selector)
                    
                    if link_element:
                        # Check if link is visible and clickable
                        is_visible = await link_element.is_visible()
                        if is_visible:
                            # Click the link
                            await link_element.click()
                            
                            # Wait for navigation or page change
                            await page.wait_for_timeout(3000)  # Wait 3 seconds
                            
                            # Log current URL
                            current_url = page.url
                            logger.info(f"Current URL after click: {current_url}")
                            
                            # Go back to original page for next link
                            await page.go_back()
                            await page.wait_for_timeout(2000)  # Wait for page to load
                            
                        else:
                            logger.warning(f"Link not visible: {info['text']}")
                    else:
                        logger.warning(f"Link element not found: {info['href']}")
                        
                except Exception as e:
                    logger.error(f"Error clicking link {i}: {e}")
                    continue
                
                # Small delay between clicks
                await page.wait_for_timeout(1000)
            
            logger.info("Finished clicking all links")
            
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        
        finally:
            # Close browser
            await context.close()
            await browser.close()

@click.command()
@click.option('--url', '-u', default='https://www.video-jungle.com', 
              help='URL to visit and click all links on')
@click.option('--headless', '-h', is_flag=True, default=False,
              help='Run in headless mode (no visible browser)')
def main(url, headless):
    """Main function to run the link clicker"""
    async def run_async():
        try:
            await click_all_links(url, headless)
        except KeyboardInterrupt:
            logger.info("Script interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
    
    asyncio.run(run_async())

if __name__ == "__main__":
    # Install required packages first:
    # pip install playwright click
    # playwright install chromium
    
    main()