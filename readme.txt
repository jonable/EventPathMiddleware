EventPath Middleware.

Sync orders from SER's online storefronts, with SER's offline proprietary ERP (EventPath). 

Background:
This django web application was responsible for pulling orders from an online storefront/ecommerce site, mapping the online orders to the offline ones, then pushing them into SER's proprietary ERP (EventPath) in a one way data flow.

Data was origanlly processed through a JSON file dumped from the online store and then uploaded into EPMiddleware web application's interface. 

Eventually this was automated, however the module used for this is missing from this repo. The online storefront was a closed source web app, which stopped development and required using selenium to download the data from the site.

This application was retired with EventPath.

