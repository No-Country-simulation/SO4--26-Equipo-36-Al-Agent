const puppeteer = require('puppeteer');
(async () => {
    const browser = await puppeteer.launch({headless: 'new', args: ['--no-sandbox']});
    const page = await browser.newPage();
    await page.goto('http://localhost:8000/chat', {waitUntil: 'networkidle0'});
    
    // Get the bounding boxes of the header, history, and input
    const layout = await page.evaluate(() => {
        const header = document.querySelector('.bg-brand-obsidian.p-4.border-b-2');
        const history = document.getElementById('chat-history');
        const input = document.querySelector('.p-4.bg-brand-obsidian.border-t-2');
        const main = document.querySelector('main');
        const core = document.querySelector('[hx-ext="ws"]');
        
        return {
            main: main ? main.getBoundingClientRect() : null,
            core: core ? core.getBoundingClientRect() : null,
            core_classes: core ? core.className : null,
            core_display: core ? window.getComputedStyle(core).display : null,
            core_flexDirection: core ? window.getComputedStyle(core).flexDirection : null,
            header: header ? header.getBoundingClientRect() : null,
            history: history ? history.getBoundingClientRect() : null,
            input: input ? input.getBoundingClientRect() : null
        };
    });
    console.log(JSON.stringify(layout, null, 2));
    await browser.close();
})();
