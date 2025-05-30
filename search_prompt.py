search_prompt = '''
Your task is to generate descriptions for a product. 

The description should contain all the available information needed for a user
in order to decide whether to buy the product or not and should be as descriptive as possible.

For example you can include the following information:

* Quality & Craftsmanship: grade of materials, build process, certifications (e.g., ISO, GOTS, Fair-Trade), expected lifespan.

* Key Features & Technology: standout functionalities, patent-pending elements, special coatings, software versions, sensors, etc.

* Specifications:  dimensions, weight, capacity/volume, power requirements, compatibility lists, model numbers.

* Materials & Ingredients: type, origin, sustainability info, hypoallergenic/vegan status, recyclability.

* Performance Metrics: speed, accuracy, battery life, energy efficiency ratings, benchmark results, lab-tested outcomes.

* Benefits to the User: how each feature solves a real pain-point; emphasise measurable improvements (e.g., “cools a 25 m² room 40 % faster”).

* Use-case Scenarios: practical examples or mini-stories showing the product in context.

* What’s in the Box: list every accessory, cable, manual, or bonus item.

* Setup & Maintenance: installation steps, required tools, cleaning/care instructions, software updates.

* Safety & Compliance: certifications (UL, CE, FCC, FDA), child-safety mechanisms, allergen statements.

* Warranty & Support: coverage length, what’s included/excluded, how to claim.

* Price & Value: MSRP or price bracket, cost-of-ownership insights (e.g., “$0.03 per hour to run”), financing options.

* Comparisons & Alternatives: how it stacks up against at least one competing model.

* Customer Proof: summary of top verified-buyer praises and common objections (include numbers if possible, e.g., “4.7 ★ out of 2 134 reviews in amazon”)

* Environmental & Social Impact: carbon footprint, charitable give-backs, ethical sourcing.

* Ideal Buyer Profile – who will get the most value; mention any groups for whom it may not be suitable.

use different ecommerce websites for this purpose.

Now generate description for the following product:
'''
