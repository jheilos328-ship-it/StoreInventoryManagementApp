# Retail Inventory Management App


Overview

I designed an inventory analysis tool that identifies potential inventory problems and proposes solutions to those problems, to help businesses manage their inventory with less decision fatigue. The goal was to identify trends in inventory data and identify issues like overstock or dead products, and create quick solutions for them.


How it works

- Identifies issues across the dataset, such as dead stock, overstock, or products running out of stock using math formulas
- Scores and ranks issues with a scoring system to rank and prioritize which decisions need to be made first
- Uses AI (In this version, ollama3.2) to generate readable summaries and descriptions of the problem and how to fix it
- Important: The AI does not decide what decisions must be made - the scoring system creates and prioritizes them, while the AI makes the readable summaries to ensure reliability and consistency


Limitations and Realizations

- During the development process, I discovered that, in order to make a system that correctly identifies and prioritizes issues, it must account for a very large number of variables. Overstock and running out of stock depends on how much capacity the store has for a specific product, a budget for a product, or how often the budget may change. For example, perishable products like milk can require separate rules because of expiration dates and how often restocks occur. That is why building an application like this makes targeting a specific niche that sells a specific product type appropriate, because it would allow me to build a rule system that accounts for a specific set of needs. Accounting for all these variables can be a challenge when creating a logic-dependent codebase, however, this kind of engineering is something I'd like to improve on in the future.
- Through cold-calling retail businesses, I had an important realization. Retailers often change their stock seasonally, meaning past sales data doesn't always represent the current state of the inventory. Since my project relies on past data trends to make predictive inventory decisions, the decision making may be inaccurate or may not have enough relevant historical data to refer to.


