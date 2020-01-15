## What is BikeData Vancouver?
BikeData Vancouver is a dashboard that allows users to explore the [official system data](https://www.mobibikes.ca/en/system-data) supplied by the [Mobi bikeshare company](https://www.mobibikes.ca/). BikeData Vancouver is not associated with or endorsed by Mobi.

## How do I use this site?
Click the calendar icon to select at date or date range and choose the membership types you're interested in. If you've zoomed in on a date range, that date range will be pre-selected.

Click on a station in the station map to further filter by trips starting and/or ending at that station.

## Who made this?
BikeData Vancouver is created by me, Mike Jarrett. I'm a data scientist and bike enthusiast in Vancouver BC. I'm on twitter at [@mikejarrett_](http://twitter.com/mikejarrett_) and I can be reached by email at mike~at~mikejarrett.ca.

## What data preparation did you do?
I do a small amount of data cleaning when importing the trip records. Some records in the data set start or stop at Mobi's workshop, so I exclude those. I also exclude records with missing station or membership information. Finally, I drop trips shorter than 60s which begin and and at the same station. At the time of writing, that works our to droping about 3% of records in the dataset. These are all fairly arbitrary choices so if you are comparing numbers on this site to other sources there may be some discrepancies. If there is a difference between any numbers on this site and numbers provided by Mobi or the City of Vancouver, you should trust the official sources first (but please let me know about it!)

If you would like more details about data preparation, please get in touch and I can provide my processing logs.

## Is this project related to [@VanBikeShareBot](http://twitter.com/vanbikesharebot)?
Yes, in that they're both created by me. The twitter bot does real time trip estimates, while this website contains official trip records from Mobi. There is some variance (up to ~10%) between the daily estimates and the official stats.

## What other bikeshare content do you have?
I occasional post about bikeshare use on my [blog](http://notes.mikejarrett.ca).

## Where can I submit bug reports?
Feel free to submit bug reports on the project's [github page](https://github.com/mjarrett/bikedata-vancouver).