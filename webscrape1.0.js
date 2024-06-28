const puppeteer = require('puppeteer');

let scrape = async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();

  const searchQuery = 'Charot';  
  const twitterSearchUrl = `https://twitter.com/search?q=${encodeURIComponent(searchQuery)}&src=typed_query`;

  try {
    await page.goto(twitterSearchUrl, { waitUntil: 'networkidle2' });

    // Wait for tweets to load
    await page.waitForSelector('article');

    const tweets = await page.evaluate(() => {
      const tweetElements = document.querySelectorAll('article');
      const tweetData = [];

      tweetElements.forEach(el => {
        let username = el.querySelector('div[dir="ltr"] span').textContent.trim();
        let handle = el.querySelector('div[dir="ltr"] a').getAttribute('href').replace('/', '@');
        let content = el.querySelector('div[lang]').textContent.trim();
        let timestamp = el.querySelector('time')?.getAttribute('datetime');

        tweetData.push({
          username,
          handle,
          content,
          timestamp
        });
      });

      return tweetData;
    });

    return tweets;
  } catch (error) {
    console.error('Error:', error);
    return [];
  } finally {
    await browser.close();
  }
};

scrape().then((tweets) => {
  console.log(tweets);
});
