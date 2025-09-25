"""
Order Schema for Text-to-Order Feature
Defines data structures for order items, modifications, and complete orders
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from decimal import Decimal


class SizeType(str, Enum):
    """Available item sizes"""
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    EXTRA_LARGE = "Extra Large"


class ModificationType(str, Enum):
    """Types of modifications"""
    ADD = "add"
    REMOVE = "remove"
    SUBSTITUTE = "substitute"
    EXTRA = "extra"
    ON_SIDE = "on_side"


class Modification(BaseModel):
    """Individual modification to an order item"""
    type: ModificationType
    item: str
    description: Optional[str] = None
    price_change: Decimal = Field(default=Decimal('0.00'))
    
    class Config:
        use_enum_values = True


class OrderItem(BaseModel):
    """Individual item in an order"""
    name: str = Field(..., description="Name of the menu item")
    quantity: int = Field(default=1, ge=1, description="Quantity ordered")
    size: Optional[SizeType] = Field(default=None, description="Size if applicable")
    base_price: Decimal = Field(default=Decimal('0.00'), description="Base price for the item")
    modifications: List[Modification] = Field(default_factory=list, description="Modifications to the item")
    special_instructions: Optional[str] = Field(default=None, description="Special preparation instructions")
    
    @property
    def total_price(self) -> Decimal:
        """Calculate total price including modifications"""
        mod_price = sum(mod.price_change for mod in self.modifications)
        return (self.base_price + mod_price) * self.quantity
    
    class Config:
        use_enum_values = True


class Order(BaseModel):
    """Complete order containing multiple items"""
    items: List[OrderItem] = Field(default_factory=list, description="Items in the order")
    customer_notes: Optional[str] = Field(default=None, description="Special notes from customer")
    estimated_time: Optional[int] = Field(default=None, description="Estimated preparation time in minutes")
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate order subtotal"""
        return sum(item.total_price for item in self.items)
    
    @property
    def tax_amount(self, tax_rate: Decimal = Decimal('0.08')) -> Decimal:
        """Calculate tax amount (default 8%)"""
        return self.subtotal * tax_rate
    
    @property
    def total_amount(self, tax_rate: Decimal = Decimal('0.08')) -> Decimal:
        """Calculate total amount including tax"""
        return self.subtotal + self.tax_amount
    
    @property
    def item_count(self) -> int:
        """Total number of items in order"""
        return sum(item.quantity for item in self.items)


class MenuItemTemplate(BaseModel):
    """Template for menu items with pricing and options"""
    name: str
    category: str
    base_price: Decimal
    available_sizes: List[SizeType] = Field(default_factory=list)
    size_pricing: Dict[str, Decimal] = Field(default_factory=dict)  # Size -> additional price
    available_modifications: List[str] = Field(default_factory=list)
    modification_pricing: Dict[str, Decimal] = Field(default_factory=dict)  # Modification -> price change
    keywords: List[str] = Field(default_factory=list)  # Alternative names/keywords
    
    class Config:
        use_enum_values = True


class OrderSchema:
    """Schema validation and utilities for orders"""
    
    # Common size keywords
    SIZE_KEYWORDS = {
        'small': SizeType.SMALL,
        'sm': SizeType.SMALL,
        'medium': SizeType.MEDIUM,
        'med': SizeType.MEDIUM,
        'm': SizeType.MEDIUM,
        'large': SizeType.LARGE,
        'lg': SizeType.LARGE,
        'l': SizeType.LARGE,
        'extra large': SizeType.EXTRA_LARGE,
        'xl': SizeType.EXTRA_LARGE,
        'jumbo': SizeType.EXTRA_LARGE
    }
    
    # Common modification keywords
    MODIFICATION_KEYWORDS = {
        'add': ModificationType.ADD,
        'extra': ModificationType.EXTRA,
        'remove': ModificationType.REMOVE,
        'no': ModificationType.REMOVE,
        'without': ModificationType.REMOVE,
        'substitute': ModificationType.SUBSTITUTE,
        'replace': ModificationType.SUBSTITUTE,
        'on the side': ModificationType.ON_SIDE,
        'side': ModificationType.ON_SIDE
    }
    
    # Quantity keywords
    QUANTITY_KEYWORDS = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'a': 1, 'an': 1, 'single': 1, 'double': 2, 'triple': 3
    }
    
    @classmethod
    def normalize_size(cls, size_text: str) -> Optional[SizeType]:
        """Normalize size text to SizeType enum"""
        if not size_text:
            return None
        return cls.SIZE_KEYWORDS.get(size_text.lower().strip())
    
    @classmethod
    def normalize_modification_type(cls, mod_text: str) -> ModificationType:
        """Normalize modification text to ModificationType enum"""
        if not mod_text:
            return ModificationType.ADD
        return cls.MODIFICATION_KEYWORDS.get(mod_text.lower().strip(), ModificationType.ADD)
    
    @classmethod
    def extract_quantity(cls, text: str) -> int:
        """Extract quantity from text"""
        text_lower = text.lower().strip()
        
        # Check for number keywords
        for word, qty in cls.QUANTITY_KEYWORDS.items():
            if word in text_lower:
                return qty
        
        # Look for digits
        import re
        numbers = re.findall(r'\b(\d+)\b', text)
        if numbers:
            return int(numbers[0])
        
        return 1  # Default quantity
    
    @classmethod
    def is_valid_order_item(cls, item: Dict[str, Any]) -> bool:
        """Validate order item data"""
        required_fields = ['name']
        return all(field in item for field in required_fields)
    
    @classmethod
    def create_sample_menu(cls) -> List[MenuItemTemplate]:
        """Create comprehensive sample menu for testing"""
        return [
            MenuItemTemplate(
                name="Caramel Ribbon Crunch Frappuccino® Blended Beverage",
                category="Beverage",
                base_price=Decimal("5.95"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['crunch frappuccino® blended', 'beverage', 'ribbon crunch frappuccino® blended beverage', 'caramel ribbon', 'caramel ribbon crunch', 'ribbon crunch frappuccino®', 'blended beverage', 'caramel', 'caramel ribbon crunch frappuccino® blended', 'crunch frappuccino® blended beverage', 'frap', 'ribbon', 'caramel ribbon crunch frappuccino®', 'frappuccino® blended', 'blended', 'ribbon crunch frappuccino® blended', 'frappuccino®', 'crunch', 'ribbon crunch', 'frapp', 'frappuccino® blended beverage', 'crunch frappuccino®']
            ),
            MenuItemTemplate(
                name="Cinnamon Dolce Latte",
                category="Beverage",
                base_price=Decimal("5.65"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['extra foam', 'extra shot', 'extra hot', 'decaf'],
                modification_pricing={
                "extra foam": Decimal("0.50"),
                "extra shot": Decimal("0.50"),
                "extra hot": Decimal("0.50"),
                "decaf": Decimal("0.00"),
            },
                keywords=['cinnamon', 'cinnamon dolce', 'latte', 'dolce latte', 'dolce']
            ),
            MenuItemTemplate(
                name="Mango Dragonfruit Starbucks Refreshers® Beverage",
                category="Main Dish",
                base_price=Decimal("4.55"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['dragonfruit starbucks refreshers® beverage', 'mango', 'refreshers® beverage', 'starbucks', 'mango dragonfruit', 'dragonfruit starbucks', 'starbucks refreshers®', 'dragonfruit starbucks refreshers®', 'starbucks refreshers® beverage', 'beverage', 'mango dragonfruit starbucks', 'dragonfruit', 'refreshers®', 'mango dragonfruit starbucks refreshers®']
            ),
            MenuItemTemplate(
                name="Iced Caramel Macchiato",
                category="Main Dish",
                base_price=Decimal("5.15"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['iced', 'caramel', 'macchiato', 'mach', 'caramel macchiato', 'iced caramel']
            ),
            MenuItemTemplate(
                name="Banana, Walnut &amp; Pecan Loaf",
                category="Main Dish",
                base_price=Decimal("3.95"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['walnut &amp;', 'walnut &amp; pecan loaf', 'pecan loaf', 'pecan', 'loaf', 'walnut', 'banana,', 'banana, walnut', 'walnut &amp; pecan', '&amp; pecan', '&amp; pecan loaf', 'banana, walnut &amp;', '&amp;', 'banana, walnut &amp; pecan']
            ),
            MenuItemTemplate(
                name="Caffè Americano",
                category="Main Dish",
                base_price=Decimal("3.15"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['american coffee', 'caffè', 'americano']
            ),
            MenuItemTemplate(
                name="Veranda Blend®",
                category="Beverage",
                base_price=Decimal("2.95"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['veranda', 'blend®']
            ),
            MenuItemTemplate(
                name="Caffè Misto",
                category="Beverage",
                base_price=Decimal("3.75"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['misto', 'caffè']
            ),
            MenuItemTemplate(
                name="Featured Starbucks® Dark Roast Coffee",
                category="Beverage",
                base_price=Decimal("2.95"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['extra foam', 'extra shot', 'extra hot', 'decaf'],
                modification_pricing={
                "extra foam": Decimal("0.50"),
                "extra shot": Decimal("0.50"),
                "extra hot": Decimal("0.50"),
                "decaf": Decimal("0.00"),
            },
                keywords=['coffee', 'starbucks® dark roast', 'featured starbucks® dark roast', 'dark', 'roast coffee', 'starbucks® dark roast coffee', 'featured starbucks®', 'featured', 'starbucks® dark', 'starbucks®', 'dark roast', 'roast', 'featured starbucks® dark', 'dark roast coffee']
            ),
            MenuItemTemplate(
                name="Pike Place® Roast",
                category="Beverage",
                base_price=Decimal("2.95"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['place®', 'pike place®', 'pike', 'roast', 'place® roast']
            ),
            MenuItemTemplate(
                name="Decaf Pike Place® Roast",
                category="Beverage",
                base_price=Decimal("2.95"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['place®', 'decaf pike', 'pike place® roast', 'decaf pike place®', 'pike place®', 'pike', 'decaf', 'roast', 'place® roast']
            ),
            MenuItemTemplate(
                name="Cappuccino",
                category="Main Dish",
                base_price=Decimal("4.25"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['capp']
            ),
            MenuItemTemplate(
                name="Flat White",
                category="Beverage",
                base_price=Decimal("4.95"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['flat', 'white']
            ),
            MenuItemTemplate(
                name="Honey Almondmilk Flat White",
                category="Main Dish",
                base_price=Decimal("5.95"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['honey almondmilk', 'almondmilk', 'honey', 'honey almondmilk flat', 'flat white', 'almondmilk flat white', 'flat', 'almondmilk flat', 'white']
            ),
            MenuItemTemplate(
                name="Caffè Latte",
                category="Beverage",
                base_price=Decimal("4.25"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['extra foam', 'extra shot', 'extra hot', 'decaf'],
                modification_pricing={
                "extra foam": Decimal("0.50"),
                "extra shot": Decimal("0.50"),
                "extra hot": Decimal("0.50"),
                "decaf": Decimal("0.00"),
            },
                keywords=['latte', 'caffè']
            ),
            MenuItemTemplate(
                name="Beefy Melt Burrito",
                category="Sandwich",
                base_price=Decimal("2.4"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['melt burrito', 'melt', 'burito', 'beefy melt', 'burrito', 'beefy']
            ),
            MenuItemTemplate(
                name="Chicken Quesadilla",
                category="Main Dish",
                base_price=Decimal("5.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['quesadila', 'quesadilla', 'chicken', 'quesa']
            ),
            MenuItemTemplate(
                name="Quesarito",
                category="Sandwich",
                base_price=Decimal("4.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=[]
            ),
            MenuItemTemplate(
                name="Crunchwrap Supreme®",
                category="Salad",
                base_price=Decimal("5.15"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['supreme®', 'crunchwrap']
            ),
            MenuItemTemplate(
                name="Blue Raspberry Freeze",
                category="Main Dish",
                base_price=Decimal("3.47"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['freeze', 'blue raspberry', 'raspberry freeze', 'blue', 'raspberry']
            ),
            MenuItemTemplate(
                name="Toasted Cheddar Chalupa",
                category="Salad",
                base_price=Decimal("5.15"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['toasted', 'toasted cheddar', 'cheddar', 'chalupa', 'cheddar chalupa']
            ),
            MenuItemTemplate(
                name="Black Bean Toasted Cheddar Chalupa",
                category="Salad",
                base_price=Decimal("5.15"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['bean', 'black bean toasted cheddar', 'toasted', 'bean toasted', 'bean toasted cheddar chalupa', 'toasted cheddar', 'toasted cheddar chalupa', 'cheddar', 'chalupa', 'black', 'black bean toasted', 'black bean', 'cheddar chalupa', 'bean toasted cheddar']
            ),
            MenuItemTemplate(
                name="Toasted Cheddar Chalupa Deluxe Box",
                category="Beverage",
                base_price=Decimal("8.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['cheddar chalupa deluxe box', 'toasted', 'toasted cheddar chalupa', 'toasted cheddar', 'deluxe box', 'cheddar', 'chalupa deluxe', 'cheddar chalupa deluxe', 'deluxe', 'chalupa', 'toasted cheddar chalupa deluxe', 'chalupa deluxe box', 'box', 'cheddar chalupa']
            ),
            MenuItemTemplate(
                name="Toasted Cheddar Chalupa Box",
                category="Beverage",
                base_price=Decimal("6.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['toasted', 'toasted cheddar chalupa', 'toasted cheddar', 'cheddar', 'chalupa box', 'chalupa', 'cheddar chalupa box', 'box', 'cheddar chalupa']
            ),
            MenuItemTemplate(
                name="Brisk® Dragon Paradise™ Sparkling Iced Tea",
                category="Beverage",
                base_price=Decimal("2.39"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['dragon paradise™ sparkling iced tea', 'brisk® dragon paradise™', 'iced', 'dragon', 'paradise™', 'brisk® dragon paradise™ sparkling iced', 'brisk® dragon paradise™ sparkling', 'dragon paradise™', 'brisk®', 'paradise™ sparkling iced', 'dragon paradise™ sparkling iced', 'sparkling iced', 'iced tea', 'tea', 'dragon paradise™ sparkling', 'ice tea', 'sparkling iced tea', 'paradise™ sparkling', 'brisk® dragon', 'sparkling', 'paradise™ sparkling iced tea']
            ),
            MenuItemTemplate(
                name="Dole® Lemonade Strawberry Squeeze",
                category="Main Dish",
                base_price=Decimal("2.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['strawberry', 'squeeze', 'lemonade', 'dole® lemonade strawberry', 'lemonade strawberry squeeze', 'lemonade strawberry', 'strawberry squeeze', 'dole®', 'dole® lemonade']
            ),
            MenuItemTemplate(
                name="Taco &amp; Burrito Cravings Pack",
                category="Main Dish",
                base_price=Decimal("15.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['taco &amp;', 'taco &amp; burrito', 'cravings', 'burrito cravings', 'pack', 'taco', '&amp; burrito cravings pack', 'cravings pack', 'taco &amp; burrito cravings', 'burito', '&amp; burrito cravings', '&amp; burrito', 'burrito cravings pack', '&amp;', 'burrito']
            ),
            MenuItemTemplate(
                name="Taco Party Pack",
                category="Main Dish",
                base_price=Decimal("20.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['party', 'taco party', 'pack', 'taco', 'party pack']
            ),
            MenuItemTemplate(
                name="Soft Taco Party Pack",
                category="Main Dish",
                base_price=Decimal("20.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['party', 'taco party', 'pack', 'taco', 'soft taco party', 'party pack', 'soft taco', 'taco party pack', 'soft']
            ),
            MenuItemTemplate(
                name="Supreme Taco Party Pack",
                category="Main Dish",
                base_price=Decimal("26.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['party', 'taco party', 'supreme taco', 'pack', 'taco', 'party pack', 'supreme', 'taco party pack', 'supreme taco party']
            ),
            MenuItemTemplate(
                name="Chick-fil-A® Sandwich Meal",
                category="Main Dish",
                base_price=Decimal("9.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['sandwich meal', 'chick-fil-a®', 'meal', 'chick-fil-a® sandwich', 'sandwich']
            ),
            MenuItemTemplate(
                name="Chick-fil-A® Nuggets",
                category="Main Dish",
                base_price=Decimal("5.69"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['chick-fil-a®', 'nuggets']
            ),
            MenuItemTemplate(
                name="Chick-fil-A® Nuggets Meal",
                category="Main Dish",
                base_price=Decimal("10.09"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['nuggets', 'nuggets meal', 'chick-fil-a® nuggets', 'chick-fil-a®', 'meal']
            ),
            MenuItemTemplate(
                name="Chick-fil-A® Deluxe Meal",
                category="Main Dish",
                base_price=Decimal("10.89"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['deluxe', 'chick-fil-a®', 'chick-fil-a® deluxe', 'meal', 'deluxe meal']
            ),
            MenuItemTemplate(
                name="Chick-fil-A® Spicy Chicken Sandwich Meal",
                category="Main Dish",
                base_price=Decimal("10.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chick-fil-a® spicy', 'chicken sandwich meal', 'chicken sand', 'chick-fil-a® spicy chicken', 'sandwich meal', 'chicken sandwich', 'chick sandwich', 'chicken', 'chick-fil-a®', 'chick-fil-a® spicy chicken sandwich', 'spicy chicken sandwich meal', 'spicy', 'meal', 'spicy chicken sandwich', 'spicy chicken', 'sandwich']
            ),
            MenuItemTemplate(
                name="Spicy Chicken Sandwich Deluxe Meal",
                category="Main Dish",
                base_price=Decimal("11.29"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['spicy chicken sandwich deluxe', 'chicken sandwich deluxe', 'chicken sand', 'sandwich deluxe', 'chicken sandwich', 'chick sandwich', 'deluxe', 'chicken', 'spicy', 'meal', 'spicy chicken sandwich', 'sandwich deluxe meal', 'spicy chicken', 'sandwich', 'chicken sandwich deluxe meal', 'deluxe meal']
            ),
            MenuItemTemplate(
                name="Grilled Chicken Sandwich Meal",
                category="Main Dish",
                base_price=Decimal("12.15"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['chicken sandwich meal', 'chicken sand', 'grilled chicken sandwich', 'sandwich meal', 'chicken sandwich', 'chick sandwich', 'grilled chicken', 'chicken', 'meal', 'sandwich', 'grilled']
            ),
            MenuItemTemplate(
                name="Grilled Chicken Club Meal",
                category="Main Dish",
                base_price=Decimal("14.15"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'bacon', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "bacon": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['chicken club meal', 'grilled chicken club', 'grilled chicken', 'chicken club', 'chicken', 'club meal', 'meal', 'club', 'grilled']
            ),
            MenuItemTemplate(
                name="Grilled Nuggets Meal",
                category="Main Dish",
                base_price=Decimal("11.15"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['nuggets', 'nuggets meal', 'grilled nuggets', 'meal', 'grilled']
            ),
            MenuItemTemplate(
                name="Chick-n-Strips® Meal",
                category="Main Dish",
                base_price=Decimal("10.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['meal', 'chick-n-strips®']
            ),
            MenuItemTemplate(
                name="Chick-fil-A® Cool Wrap Meal",
                category="Main Dish",
                base_price=Decimal("13.89"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['cool wrap meal', 'cool', 'chick-fil-a® cool', 'wrap meal', 'chick-fil-a®', 'wrap', 'meal', 'chick-fil-a® cool wrap', 'cool wrap']
            ),
            MenuItemTemplate(
                name="Chick-fil-A® Chicken Sandwich",
                category="Main Dish",
                base_price=Decimal("5.3"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sand', 'chicken sandwich', 'chick sandwich', 'chicken', 'chick-fil-a®', 'chick-fil-a® chicken', 'sandwich']
            ),
            MenuItemTemplate(
                name="Chick-fil-A® Deluxe Sandwich",
                category="Main Dish",
                base_price=Decimal("6.2"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['deluxe sandwich', 'deluxe', 'chick-fil-a®', 'chick-fil-a® deluxe', 'sandwich']
            ),
            MenuItemTemplate(
                name="Spicy Chicken Sandwich",
                category="Main Dish",
                base_price=Decimal("5.76"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sand', 'chicken sandwich', 'chick sandwich', 'chicken', 'spicy', 'spicy chicken', 'sandwich']
            ),
            MenuItemTemplate(
                name="Spicy Deluxe Sandwich",
                category="Main Dish",
                base_price=Decimal("6.66"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['spicy deluxe', 'deluxe sandwich', 'deluxe', 'spicy', 'sandwich']
            ),
            MenuItemTemplate(
                name="10 PC. Crispy Chicken Nuggets",
                category="Main Dish",
                base_price=Decimal("4.69"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['nugs', 'nuggets', 'chicken nugs', 'crispy', 'crispy chicken nuggets', 'pc.', '10 pc. crispy', 'pc. crispy chicken', '10 pc.', 'chicken', '10 pc. crispy chicken', 'chicken nuggets', 'pc. crispy', 'crispy chicken', '10', 'pc. crispy chicken nuggets']
            ),
            MenuItemTemplate(
                name="Dave's Combo",
                category="Salad",
                base_price=Decimal("8.92"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['combo', "dave's"]
            ),
            MenuItemTemplate(
                name="Baconator®",
                category="Dessert",
                base_price=Decimal("7.74"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'bacon', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "bacon": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=[]
            ),
            MenuItemTemplate(
                name="10 PC. Spicy Chicken Nuggets",
                category="Main Dish",
                base_price=Decimal("4.69"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['nugs', 'nuggets', 'chicken nugs', '10 pc. spicy chicken', 'pc. spicy chicken', 'pc.', '10 pc. spicy', '10 pc.', 'chicken', 'spicy chicken nuggets', 'pc. spicy', 'chicken nuggets', 'spicy', '10', 'spicy chicken', 'pc. spicy chicken nuggets']
            ),
            MenuItemTemplate(
                name="Dave's Double®",
                category="Salad",
                base_price=Decimal("6.57"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=["dave's", 'double®']
            ),
            MenuItemTemplate(
                name="Classic Chicken Sandwich Combo",
                category="Main Dish",
                base_price=Decimal("8.45"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['chicken sand', 'classic chicken', 'classic chicken sandwich', 'chicken sandwich', 'chick sandwich', 'chicken', 'chicken sandwich combo', 'classic', 'combo', 'sandwich combo', 'sandwich']
            ),
            MenuItemTemplate(
                name="Grilled Chicken Sandwich Combo",
                category="Main Dish",
                base_price=Decimal("8.8"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sand', 'grilled chicken sandwich', 'chicken sandwich', 'chick sandwich', 'grilled chicken', 'chicken', 'chicken sandwich combo', 'combo', 'sandwich combo', 'sandwich', 'grilled']
            ),
            MenuItemTemplate(
                name="Spicy Chicken Sandwich Combo",
                category="Main Dish",
                base_price=Decimal("8.92"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['chicken sand', 'chicken sandwich', 'chick sandwich', 'chicken', 'chicken sandwich combo', 'spicy', 'spicy chicken sandwich', 'combo', 'sandwich combo', 'spicy chicken', 'sandwich']
            ),
            MenuItemTemplate(
                name="Big Bacon Classic® Combo",
                category="Salad",
                base_price=Decimal("10.09"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'bacon', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "bacon": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['big bacon', 'big', 'bacon', 'classic® combo', 'big bacon classic®', 'bacon classic®', 'bacon classic® combo', 'classic®', 'combo']
            ),
            MenuItemTemplate(
                name="Big Bacon Cheddar Cheeseburger Combo",
                category="Burger",
                base_price=Decimal("10.09"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon', 'extra sauce', 'no onions', 'cheese', 'extra cheese', 'no pickles'],
                modification_pricing={
                "bacon": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['big bacon', 'cheesburger', 'big', 'cheddar cheeseburger', 'bacon', 'bacon cheddar cheeseburger', 'big bacon cheddar cheeseburger', 'cheeseburger combo', 'cheddar', 'cheddar cheeseburger combo', 'cheese burger', 'bacon cheddar', 'bacon cheddar cheeseburger combo', 'combo', 'big bacon cheddar', 'cheeseburger']
            ),
            MenuItemTemplate(
                name="Bourbon Bacon Cheeseburger Combo",
                category="Burger",
                base_price=Decimal("9.74"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon', 'extra sauce', 'no onions', 'cheese', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "bacon": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['bourbon bacon', 'cheesburger', 'cheeseburger combo', 'bacon', 'bacon cheeseburger', 'bourbon', 'cheese burger', 'combo', 'bourbon bacon cheeseburger', 'bacon cheeseburger combo', 'cheeseburger']
            ),
            MenuItemTemplate(
                name="Asiago Ranch Chicken Club Combo",
                category="Main Dish",
                base_price=Decimal("10.09"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'bacon', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "bacon": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['asiago ranch chicken club', 'ranch chicken', 'ranch chicken club combo', 'chicken club', 'ranch chicken club', 'chicken', 'club', 'asiago ranch chicken', 'club combo', 'combo', 'chicken club combo', 'asiago', 'ranch', 'asiago ranch']
            ),
            MenuItemTemplate(
                name="Big Bacon Cheddar Chicken Combo",
                category="Main Dish",
                base_price=Decimal("10.09"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'bacon'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "bacon": Decimal("0.00"),
            },
                keywords=['big bacon', 'big', 'bacon cheddar chicken', 'cheddar chicken', 'bacon', 'cheddar', 'chicken', 'bacon cheddar', 'combo', 'cheddar chicken combo', 'bacon cheddar chicken combo', 'big bacon cheddar', 'chicken combo', 'big bacon cheddar chicken']
            ),
            MenuItemTemplate(
                name="Hot Honey Chicken Combo",
                category="Main Dish",
                base_price=Decimal("9.62"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'bacon', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "bacon": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['hot honey', 'hot', 'honey', 'hot honey chicken', 'honey chicken', 'honey chicken combo', 'chicken', 'combo', 'chicken combo']
            ),
            MenuItemTemplate(
                name="2 Spicy Chickens, 2 JBCs &amp; 4 SM Fries",
                category="Side Dish",
                base_price=Decimal("17.63"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['no salt', 'extra crispy', 'extra salt', 'sauce'],
                modification_pricing={
                "no salt": Decimal("0.00"),
                "extra crispy": Decimal("0.50"),
                "extra salt": Decimal("0.50"),
                "sauce": Decimal("0.00"),
            },
                keywords=['spicy chickens, 2 jbcs &amp;', 'spicy chickens, 2', 'chickens,', 'jbcs', '2 spicy chickens, 2 jbcs &amp; 4', 'chickens, 2', '2 spicy chickens, 2', 'chickens, 2 jbcs &amp; 4', 'spicy chickens, 2 jbcs &amp; 4 sm fries', '&amp; 4', '4 sm fries', '2', 'jbcs &amp; 4 sm fries', '2 jbcs', '2 jbcs &amp; 4 sm', 'sm fries', 'chickens, 2 jbcs', '2 jbcs &amp;', '4 sm', 'spicy chickens,', 'chickens, 2 jbcs &amp;', 'spicy chickens, 2 jbcs', '2 jbcs &amp; 4', '2 spicy chickens, 2 jbcs &amp; 4 sm', '&amp; 4 sm', 'chickens, 2 jbcs &amp; 4 sm', 'fries', '2 spicy chickens, 2 jbcs', 'spicy chickens, 2 jbcs &amp; 4', '4', '2 jbcs &amp; 4 sm fries', 'spicy', '2 spicy chickens,', 'jbcs &amp;', 'sm', '&amp; 4 sm fries', 'spicy chickens, 2 jbcs &amp; 4 sm', '2 spicy', '2 spicy chickens, 2 jbcs &amp;', 'jbcs &amp; 4 sm', 'chickens, 2 jbcs &amp; 4 sm fries', '&amp;', 'jbcs &amp; 4']
            ),
            MenuItemTemplate(
                name="Chicken Strip Basket - 6pc",
                category="Side Dish",
                base_price=Decimal("11.7"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['basket -', '6pc', 'basket - 6pc', 'strip basket - 6pc', 'strip basket', 'strip basket -', 'chicken', 'chicken strip basket', 'strip', 'chicken strip basket -', 'basket', '- 6pc', '-', 'chicken strip']
            ),
            MenuItemTemplate(
                name="Chicken Strip Basket - 4pc",
                category="Side Dish",
                base_price=Decimal("10.11"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['basket -', '4pc', 'strip basket', 'strip basket -', 'strip basket - 4pc', 'chicken', 'chicken strip basket', 'strip', 'chicken strip basket -', 'basket', 'basket - 4pc', '-', 'chicken strip', '- 4pc']
            ),
            MenuItemTemplate(
                name="Original Cheeseburger Signature Stackburger Combo",
                category="Burger",
                base_price=Decimal("8.89"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['cheesburger', 'original', 'original cheeseburger signature', 'stackburger combo', 'signature stackburger combo', 'cheeseburger signature stackburger combo', 'signature stackburger', 'original cheeseburger signature stackburger', 'signature', 'cheeseburger signature', 'cheese burger', 'cheeseburger signature stackburger', 'original cheeseburger', 'combo', 'stackburger', 'cheeseburger']
            ),
            MenuItemTemplate(
                name="Side of Cheese Curds",
                category="Dessert",
                base_price=Decimal("5.72"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['curds', 'of cheese curds', 'side', 'side of', 'of cheese', 'of', 'cheese', 'side of cheese', 'cheese curds']
            ),
            MenuItemTemplate(
                name="Chicken Strip Basket - 6pc w/Drink",
                category="Side Dish",
                base_price=Decimal("14.01"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['- 6pc w/drink', 'chicken strip basket - 6pc', 'strip basket -', 'strip', 'basket - 6pc', '-', 'strip basket - 6pc', 'chicken', 'chicken strip basket -', 'basket', 'strip basket', '6pc', 'chicken strip basket', '- 6pc', '6pc w/drink', 'basket -', 'basket - 6pc w/drink', 'w/drink', 'chicken strip', 'strip basket - 6pc w/drink']
            ),
            MenuItemTemplate(
                name="Cotton Candy BLIZZARD® Treat",
                category="Main Dish",
                base_price=Decimal("4.38"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['cotton candy', 'cotton', 'cotton candy blizzard®', 'candy blizzard®', 'blizzard®', 'blizzard® treat', 'candy blizzard® treat', 'candy', 'treat']
            ),
            MenuItemTemplate(
                name="NEW Caramel Fudge Cheesecake BLIZZARD® Treat",
                category="Dessert",
                base_price=Decimal("4.38"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['caramel fudge', 'cheesecake', 'cheesecake blizzard®', 'caramel fudge cheesecake blizzard®', 'fudge cheesecake blizzard®', 'blizzard® treat', 'new', 'new caramel', 'caramel fudge cheesecake', 'caramel', 'treat', 'fudge', 'fudge cheesecake', 'fudge cheesecake blizzard® treat', 'new caramel fudge', 'new caramel fudge cheesecake blizzard®', 'caramel fudge cheesecake blizzard® treat', 'blizzard®', 'new caramel fudge cheesecake', 'cheesecake blizzard® treat']
            ),
            MenuItemTemplate(
                name="Girl Scout® Thin Mints® BLIZZARD® Treat",
                category="Dessert",
                base_price=Decimal("4.38"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['thin', 'scout®', 'mints® blizzard®', 'mints®', 'blizzard® treat', 'thin mints® blizzard® treat', 'girl scout® thin mints®', 'scout® thin mints®', 'mints® blizzard® treat', 'scout® thin mints® blizzard®', 'thin mints®', 'treat', 'scout® thin mints® blizzard® treat', 'girl scout® thin', 'scout® thin', 'blizzard®', 'girl', 'girl scout® thin mints® blizzard®', 'thin mints® blizzard®', 'girl scout®']
            ),
            MenuItemTemplate(
                name="Nestle® DRUMSTICK® with Peanuts BLIZZARD® Treat",
                category="Dessert",
                base_price=Decimal("4.38"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['nestle® drumstick® with peanuts blizzard®', 'with', 'nestle® drumstick®', 'drumstick® with', 'blizzard® treat', 'nestle®', 'peanuts blizzard®', 'drumstick®', 'with peanuts', 'peanuts blizzard® treat', 'drumstick® with peanuts', 'treat', 'with peanuts blizzard® treat', 'peanuts', 'with peanuts blizzard®', 'drumstick® with peanuts blizzard® treat', 'nestle® drumstick® with peanuts', 'drumstick® with peanuts blizzard®', 'blizzard®', 'nestle® drumstick® with']
            ),
            MenuItemTemplate(
                name="NEW OREO® Dirt Pie BLIZZARD® Treat",
                category="Dessert",
                base_price=Decimal("4.38"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['pie blizzard®', 'pie', 'dirt pie blizzard® treat', 'blizzard® treat', 'oreo® dirt pie', 'new oreo® dirt pie', 'new', 'dirt pie blizzard®', 'new oreo® dirt pie blizzard®', 'new oreo®', 'dirt', 'dirt pie', 'oreo® dirt', 'treat', 'oreo® dirt pie blizzard®', 'blizzard®', 'oreo®', 'new oreo® dirt', 'oreo® dirt pie blizzard® treat', 'pie blizzard® treat']
            ),
            MenuItemTemplate(
                name="Very Cherry Chip BLIZZARD® Treat",
                category="Main Dish",
                base_price=Decimal("4.38"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['cherry', 'chip', 'cherry chip blizzard® treat', 'blizzard®', 'chip blizzard® treat', 'blizzard® treat', 'very cherry chip blizzard®', 'cherry chip blizzard®', 'chip blizzard®', 'very', 'cherry chip', 'very cherry', 'very cherry chip', 'treat']
            ),
            MenuItemTemplate(
                name="Chocolate Chip Cookie Dough BLIZZARD® Treat",
                category="Dessert",
                base_price=Decimal("4.38"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['chocolate chip cookie', 'chip cookie dough', 'chip cookie dough blizzard® treat', 'cookie dough blizzard®', 'blizzard® treat', 'cookie', 'chip cookie dough blizzard®', 'cookie dough', 'cookie dough blizzard® treat', 'chip cookie', 'dough blizzard® treat', 'treat', 'chocolate chip', 'chocolate', 'dough', 'dough blizzard®', 'chip', 'blizzard®', 'chocolate chip cookie dough', 'chocolate chip cookie dough blizzard®']
            ),
            MenuItemTemplate(
                name="Choco Brownie Extreme BLIZZARD® Treat",
                category="Dessert",
                base_price=Decimal("4.38"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['brownie extreme blizzard®', 'extreme', 'brownie extreme', 'choco brownie extreme blizzard®', 'blizzard®', 'brownie extreme blizzard® treat', 'blizzard® treat', 'brownie', 'choco brownie', 'extreme blizzard® treat', 'choco brownie extreme', 'extreme blizzard®', 'choco', 'treat']
            ),
            MenuItemTemplate(
                name="Turtle Pecan Cluster BLIZZARD® Treat",
                category="Dessert",
                base_price=Decimal("4.38"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['pecan cluster blizzard®', 'pecan cluster blizzard® treat', 'cluster', 'pecan cluster', 'cluster blizzard® treat', 'pecan', 'blizzard®', 'turtle pecan', 'cluster blizzard®', 'turtle pecan cluster', 'turtle pecan cluster blizzard®', 'blizzard® treat', 'turtle', 'treat']
            ),
            MenuItemTemplate(
                name="OREO® BLIZZARD® Treat",
                category="Dessert",
                base_price=Decimal("4.38"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['blizzard®', 'oreo®', 'oreo® blizzard®', 'blizzard® treat', 'treat']
            ),
            MenuItemTemplate(
                name="12 pc. Family Bucket Meal",
                category="Main Dish",
                base_price=Decimal("39.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['12', 'bucket meal', 'bucket', 'pc.', '12 pc.', 'pc. family', 'pc. family bucket meal', 'family', 'family bucket', 'meal', 'pc. family bucket', 'family bucket meal', '12 pc. family', '12 pc. family bucket']
            ),
            MenuItemTemplate(
                name="8 pc. Family Bucket Meal",
                category="Main Dish",
                base_price=Decimal("28.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['8 pc.', 'bucket meal', 'bucket', '8', 'pc.', 'pc. family bucket meal', 'pc. family', '8 pc. family bucket', 'family', 'family bucket', 'meal', '8 pc. family', 'pc. family bucket', 'family bucket meal']
            ),
            MenuItemTemplate(
                name="3 pc. Chicken Combo",
                category="Beverage",
                base_price=Decimal("9.83"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['pc.', '3 pc. chicken', 'pc. chicken', '3 pc.', 'chicken', '3', 'pc. chicken combo', 'combo', 'chicken combo']
            ),
            MenuItemTemplate(
                name="Famous Bowl",
                category="Side Dish",
                base_price=Decimal("6.35"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['famous', 'bowl']
            ),
            MenuItemTemplate(
                name="1/2 Gallon Beverage Bucket",
                category="Main Dish",
                base_price=Decimal("4.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['gallon beverage bucket', 'bucket', '1/2', 'gallon beverage', '1/2 gallon beverage', 'gallon', 'beverage', 'beverage bucket', '1/2 gallon']
            ),
            MenuItemTemplate(
                name="8 pc. Family Fill Up Bucket Meal",
                category="Side Dish",
                base_price=Decimal("31.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['8 pc. family fill up', 'family fill', 'pc. family fill up bucket', 'up', 'meal', '8 pc. family fill', 'family fill up bucket', 'up bucket meal', 'pc. family fill up bucket meal', '8', 'fill', 'family', '8 pc. family', '8 pc.', 'bucket meal', 'up bucket', 'pc. family', 'fill up bucket', 'family fill up bucket meal', 'pc. family fill', 'fill up', 'pc. family fill up', 'family fill up', '8 pc. family fill up bucket', 'bucket', 'pc.', 'fill up bucket meal']
            ),
            MenuItemTemplate(
                name="10 Piece Feast",
                category="Side Dish",
                base_price=Decimal("36.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['feast', '10 piece', 'piece', '10', 'piece feast']
            ),
            MenuItemTemplate(
                name="16 pc. Family Bucket Meal",
                category="Main Dish",
                base_price=Decimal("52.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['bucket meal', 'bucket', 'family bucket meal', 'pc.', 'pc. family bucket meal', 'pc. family', 'family', 'family bucket', 'meal', 'pc. family bucket', '16 pc. family bucket', '16 pc.', '16 pc. family', '16']
            ),
            MenuItemTemplate(
                name="Sides Lovers 8 pc. Chicken Meal",
                category="Main Dish",
                base_price=Decimal("31.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['meal', '8 pc. chicken', 'pc. chicken meal', 'lovers 8 pc.', '8', 'sides lovers 8 pc. chicken', 'chicken', 'sides lovers 8 pc.', '8 pc. chicken meal', 'chicken meal', 'lovers 8 pc. chicken', '8 pc.', 'sides lovers', 'lovers', 'pc. chicken', 'sides', 'lovers 8 pc. chicken meal', 'sides lovers 8', 'pc.', 'lovers 8']
            ),
            MenuItemTemplate(
                name="8 pc. Chicken",
                category="Main Dish",
                base_price=Decimal("20.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['8 pc.', '8', 'pc.', 'pc. chicken', 'chicken']
            ),
            MenuItemTemplate(
                name="12 pc. Chicken",
                category="Main Dish",
                base_price=Decimal("28.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['12', '12 pc.', 'pc.', 'pc. chicken', 'chicken']
            ),
            MenuItemTemplate(
                name="16 pc. Chicken",
                category="Main Dish",
                base_price=Decimal("38.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['pc.', 'pc. chicken', 'chicken', '16 pc.', '16']
            ),
            MenuItemTemplate(
                name="8 Tenders Bucket",
                category="Main Dish",
                base_price=Decimal("20.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['bucket', '8', '8 tenders', 'tenders', 'tenders bucket']
            ),
            MenuItemTemplate(
                name="12 Tenders Bucket",
                category="Main Dish",
                base_price=Decimal("28.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['12', 'bucket', '12 tenders', 'tenders', 'tenders bucket']
            ),
            MenuItemTemplate(
                name="16 Tenders Bucket",
                category="Main Dish",
                base_price=Decimal("38.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['16 tenders', 'bucket', 'tenders', 'tenders bucket', '16']
            ),
            MenuItemTemplate(
                name="Double Whopper Meal",
                category="Burger",
                base_price=Decimal("12.49"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['whopper meal', 'double whopper', 'double', 'whopper', 'meal']
            ),
            MenuItemTemplate(
                name="Whopper Meal",
                category="Burger",
                base_price=Decimal("11.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['whopper', 'meal']
            ),
            MenuItemTemplate(
                name="Family Bundle",
                category="Burger",
                base_price=Decimal("20.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['family', 'bundle']
            ),
            MenuItemTemplate(
                name="Bacon King Sandwich Meal",
                category="Sandwich",
                base_price=Decimal("13.69"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon', 'extra sauce', 'no onions', 'extra cheese', 'no pickles'],
                modification_pricing={
                "bacon": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['king', 'bacon', 'sandwich meal', 'meal', 'bacon king', 'bacon king sandwich', 'king sandwich', 'sandwich', 'king sandwich meal']
            ),
            MenuItemTemplate(
                name="Original Chicken Sandwich",
                category="Main Dish",
                base_price=Decimal("6.89"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sand', 'original', 'chicken sandwich', 'chick sandwich', 'chicken', 'sandwich', 'original chicken']
            ),
            MenuItemTemplate(
                name="Whopper Melt Meal",
                category="Burger",
                base_price=Decimal("9.58"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['melt', 'whopper melt', 'melt meal', 'whopper', 'meal']
            ),
            MenuItemTemplate(
                name="Bacon Whopper Melt Meal",
                category="Burger",
                base_price=Decimal("10.3"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'bacon'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "bacon": Decimal("0.00"),
            },
                keywords=['bacon', 'whopper melt meal', 'melt', 'bacon whopper', 'bacon whopper melt', 'whopper melt', 'melt meal', 'whopper', 'meal']
            ),
            MenuItemTemplate(
                name="Spicy Whopper Melt Meal",
                category="Burger",
                base_price=Decimal("9.58"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['spicy whopper melt', 'whopper melt meal', 'melt', 'whopper melt', 'spicy whopper', 'melt meal', 'whopper', 'spicy', 'meal']
            ),
            MenuItemTemplate(
                name="Triple Whopper Meal",
                category="Burger",
                base_price=Decimal("14.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['whopper meal', 'whopper', 'meal', 'triple whopper', 'triple']
            ),
            MenuItemTemplate(
                name="Impossible™ Whopper Meal",
                category="Burger",
                base_price=Decimal("12.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['whopper meal', 'impossible™ whopper', 'whopper', 'meal', 'impossible™']
            ),
            MenuItemTemplate(
                name="Whopper Jr. Meal",
                category="Burger",
                base_price=Decimal("8.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['jr. meal', 'whopper', 'whopper jr.', 'meal', 'jr.']
            ),
            MenuItemTemplate(
                name="Original Chicken Sandwich Meal",
                category="Main Dish",
                base_price=Decimal("10.89"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sandwich meal', 'chicken sand', 'original', 'sandwich meal', 'chicken sandwich', 'chick sandwich', 'chicken', 'meal', 'original chicken sandwich', 'sandwich', 'original chicken']
            ),
            MenuItemTemplate(
                name="9PC Chicken Fries Meal",
                category="Side Dish",
                base_price=Decimal("9.49"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['no salt', 'extra crispy', 'extra salt'],
                modification_pricing={
                "no salt": Decimal("0.00"),
                "extra crispy": Decimal("0.50"),
                "extra salt": Decimal("0.50"),
            },
                keywords=['fries', '9pc chicken fries', 'chicken fries', '9pc chicken', 'chicken', '9pc', 'meal', 'fries meal', 'chicken fries meal']
            ),
            MenuItemTemplate(
                name="8PC Chicken Nuggets Meal",
                category="Main Dish",
                base_price=Decimal("5.69"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['nugs', 'nuggets', 'chicken nugs', 'nuggets meal', '8pc', 'chicken', 'chicken nuggets meal', '8pc chicken', 'chicken nuggets', 'meal', '8pc chicken nuggets']
            ),
            MenuItemTemplate(
                name="Spicy Ch'King Sandwich Meal",
                category="Sandwich",
                base_price=Decimal("10.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['sandwich meal', "ch'king", "spicy ch'king sandwich", "ch'king sandwich meal", 'meal', 'spicy', "ch'king sandwich", "spicy ch'king", 'sandwich']
            ),
            MenuItemTemplate(
                name="Crispy Chicken Sandwich",
                category="Main Dish",
                base_price=Decimal("4.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sand', 'crispy', 'chicken sandwich', 'chick sandwich', 'chicken', 'crispy chicken', 'sandwich']
            ),
            MenuItemTemplate(
                name="Crispy Chicken Sandwich Meal",
                category="Main Dish",
                base_price=Decimal("8.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sandwich meal', 'chicken sand', 'crispy', 'sandwich meal', 'chicken sandwich', 'chick sandwich', 'crispy chicken sandwich', 'chicken', 'meal', 'crispy chicken', 'sandwich']
            ),
            MenuItemTemplate(
                name="Big Mac Meal",
                category="Main Dish",
                base_price=Decimal("9.29"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['mac meal', 'big', 'big mac', 'meal', 'mac']
            ),
            MenuItemTemplate(
                name="Double Quarter Pounder with Cheese Meal",
                category="Main Dish",
                base_price=Decimal("10.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['quarter pounder', 'double quarter pounder', 'quarter pounder with', 'quarter pounder with cheese', 'with cheese', 'with', 'double quarter', 'pounder with', 'with cheese meal', 'cheese', 'meal', 'double quarter pounder with', 'double', 'cheese meal', 'pounder', 'double quarter pounder with cheese', 'quarter pounder with cheese meal', 'pounder with cheese meal', 'pounder with cheese', 'quarter']
            ),
            MenuItemTemplate(
                name="10 Piece McNuggets Meal",
                category="Main Dish",
                base_price=Decimal("8.29"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['10 piece', 'piece mcnuggets meal', 'mcnuggets meal', '10 piece mcnuggets', 'meal', 'piece', '10', 'mcnuggets', 'piece mcnuggets']
            ),
            MenuItemTemplate(
                name="20 Piece McNuggets",
                category="Main Dish",
                base_price=Decimal("7.19"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['20', 'piece', 'mcnuggets', 'piece mcnuggets', '20 piece']
            ),
            MenuItemTemplate(
                name="40 McNuggets",
                category="Main Dish",
                base_price=Decimal("13.59"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['mcnuggets', '40']
            ),
            MenuItemTemplate(
                name="Medium French Fries",
                category="Side Dish",
                base_price=Decimal("3.19"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['no salt', 'extra crispy', 'extra salt'],
                modification_pricing={
                "no salt": Decimal("0.00"),
                "extra crispy": Decimal("0.50"),
                "extra salt": Decimal("0.50"),
            },
                keywords=['french fries', 'fries', 'medium', 'ff', 'medium french', 'french', 'fires']
            ),
            MenuItemTemplate(
                name="Regular Oreo McFlurry",
                category="Main Dish",
                base_price=Decimal("4.09"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['oreo mcflurry', 'mcflurry', 'regular', 'oreo', 'regular oreo']
            ),
            MenuItemTemplate(
                name="Medium Coke®",
                category="Beverage",
                base_price=Decimal("1.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['medium', 'coke®']
            ),
            MenuItemTemplate(
                name="Spicy Chicken Sandwich Meal",
                category="Main Dish",
                base_price=Decimal("8.49"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sandwich meal', 'chicken sand', 'sandwich meal', 'chicken sandwich', 'chick sandwich', 'chicken', 'spicy', 'meal', 'spicy chicken sandwich', 'spicy chicken', 'sandwich']
            ),
            MenuItemTemplate(
                name="Deluxe Crispy Chicken Sandwich Meal",
                category="Main Dish",
                base_price=Decimal("8.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sandwich meal', 'chicken sand', 'deluxe crispy', 'crispy', 'deluxe crispy chicken', 'sandwich meal', 'chicken sandwich', 'chick sandwich', 'crispy chicken sandwich', 'deluxe', 'chicken', 'meal', 'crispy chicken', 'deluxe crispy chicken sandwich', 'sandwich', 'crispy chicken sandwich meal']
            ),
            MenuItemTemplate(
                name="Spicy Deluxe Crispy Chicken Sandwich Meal",
                category="Main Dish",
                base_price=Decimal("9.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chick sandwich', 'crispy chicken sandwich', 'spicy deluxe', 'meal', 'chicken sand', 'deluxe crispy', 'sandwich meal', 'chicken sandwich', 'chicken', 'spicy deluxe crispy chicken sandwich', 'sandwich', 'spicy deluxe crispy', 'crispy chicken sandwich meal', 'spicy deluxe crispy chicken', 'deluxe', 'deluxe crispy chicken sandwich meal', 'spicy', 'crispy chicken', 'chicken sandwich meal', 'deluxe crispy chicken', 'crispy', 'deluxe crispy chicken sandwich']
            ),
            MenuItemTemplate(
                name="Quarter Pounder with Cheese Meal",
                category="Main Dish",
                base_price=Decimal("8.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['pounder', 'quarter pounder', 'quarter pounder with', 'quarter pounder with cheese', 'with cheese', 'with', 'pounder with', 'with cheese meal', 'cheese', 'meal', 'pounder with cheese meal', 'pounder with cheese', 'cheese meal', 'quarter']
            ),
            MenuItemTemplate(
                name="Double Bacon Quarter Pounder with Cheese Meal",
                category="Main Dish",
                base_price=Decimal("11.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'bacon'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "bacon": Decimal("0.00"),
            },
                keywords=['quarter pounder', 'quarter pounder with', 'quarter pounder with cheese', 'with cheese', 'with', 'bacon quarter pounder', 'pounder with', 'with cheese meal', 'cheese', 'meal', 'bacon', 'double', 'double bacon', 'cheese meal', 'double bacon quarter', 'double bacon quarter pounder with cheese', 'bacon quarter pounder with', 'pounder', 'bacon quarter', 'quarter pounder with cheese meal', 'double bacon quarter pounder with', 'bacon quarter pounder with cheese meal', 'pounder with cheese meal', 'double bacon quarter pounder', 'pounder with cheese', 'bacon quarter pounder with cheese', 'quarter']
            ),
            MenuItemTemplate(
                name="Coke Bottle",
                category="Beverage",
                base_price=Decimal("3.71"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['coke', 'bottle']
            ),
            MenuItemTemplate(
                name="Sprite Bottle",
                category="Beverage",
                base_price=Decimal("3.71"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['sprite', 'bottle']
            ),
            MenuItemTemplate(
                name="Simply Lemonade",
                category="Main Dish",
                base_price=Decimal("3.71"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['simply', 'lemonade']
            ),
            MenuItemTemplate(
                name="Hamburger",
                category="Burger",
                base_price=Decimal("11.87"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=[]
            ),
            MenuItemTemplate(
                name="Cheeseburger",
                category="Burger",
                base_price=Decimal("13.07"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['cheese burger', 'cheesburger']
            ),
            MenuItemTemplate(
                name="Bacon Burger",
                category="Burger",
                base_price=Decimal("13.55"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon', 'extra sauce', 'no onions', 'extra cheese', 'no pickles'],
                modification_pricing={
                "bacon": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['bacon', 'burger']
            ),
            MenuItemTemplate(
                name="Bacon Cheeseburger",
                category="Burger",
                base_price=Decimal("14.75"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon', 'extra sauce', 'no onions', 'cheese', 'extra cheese', 'no pickles'],
                modification_pricing={
                "bacon": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['cheese burger', 'cheesburger', 'bacon', 'cheeseburger']
            ),
            MenuItemTemplate(
                name="Little Hamburger",
                category="Burger",
                base_price=Decimal("8.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['little', 'hamburger']
            ),
            MenuItemTemplate(
                name="Little Cheeseburger",
                category="Burger",
                base_price=Decimal("10.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['cheese burger', 'cheesburger', 'little', 'cheeseburger']
            ),
            MenuItemTemplate(
                name="Little Bacon Burger",
                category="Burger",
                base_price=Decimal("10.67"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon', 'extra sauce', 'no onions', 'extra cheese', 'no pickles'],
                modification_pricing={
                "bacon": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['bacon', 'little', 'bacon burger', 'little bacon', 'burger']
            ),
            MenuItemTemplate(
                name="Little Bacon Cheeseburger",
                category="Burger",
                base_price=Decimal("11.87"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon', 'extra sauce', 'no onions', 'cheese', 'extra cheese', 'no pickles'],
                modification_pricing={
                "bacon": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['cheesburger', 'bacon', 'little', 'bacon cheeseburger', 'cheese burger', 'little bacon', 'cheeseburger']
            ),
            MenuItemTemplate(
                name="Kosher Style Hot Dog",
                category="Main Dish",
                base_price=Decimal("7.91"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['style hot dog', 'hot', 'style hot', 'style', 'kosher', 'kosher style', 'dog', 'kosher style hot', 'hot dog']
            ),
            MenuItemTemplate(
                name="Cheese Dog",
                category="Main Dish",
                base_price=Decimal("9.11"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['cheese', 'dog']
            ),
            MenuItemTemplate(
                name="Bacon Dog",
                category="Main Dish",
                base_price=Decimal("9.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon'],
                modification_pricing={
                "bacon": Decimal("0.00"),
            },
                keywords=['bacon', 'dog']
            ),
            MenuItemTemplate(
                name="Bacon Cheese Dog",
                category="Main Dish",
                base_price=Decimal("10.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'bacon'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "bacon": Decimal("0.00"),
            },
                keywords=['bacon', 'cheese dog', 'cheese', 'dog', 'bacon cheese']
            ),
            MenuItemTemplate(
                name="Jamocha Shake",
                category="Main Dish",
                base_price=Decimal("3.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['shake', 'jamocha']
            ),
            MenuItemTemplate(
                name="Classic Beef 'n Cheddar",
                category="Main Dish",
                base_price=Decimal("5.29"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=["'n", 'beef', 'classic beef', 'cheddar', "classic beef 'n", "beef 'n cheddar", 'classic', "beef 'n", "'n cheddar"]
            ),
            MenuItemTemplate(
                name="Classic French Dip &amp; Swiss",
                category="Sandwich",
                base_price=Decimal("6.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['dip &amp;', 'classic french dip &amp;', 'dip', 'french dip &amp; swiss', '&amp; swiss', 'french dip &amp;', 'dip &amp; swiss', 'french', 'classic', 'french dip', 'classic french dip', 'classic french', '&amp;', 'swiss']
            ),
            MenuItemTemplate(
                name="Reuben",
                category="Main Dish",
                base_price=Decimal("6.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=[]
            ),
            MenuItemTemplate(
                name="Chicken Bacon &amp; Swiss",
                category="Main Dish",
                base_price=Decimal("6.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'bacon'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "bacon": Decimal("0.00"),
            },
                keywords=['chicken bacon &amp;', 'bacon', 'bacon &amp; swiss', 'bacon &amp;', '&amp; swiss', 'chicken', '&amp;', 'swiss', 'chicken bacon']
            ),
            MenuItemTemplate(
                name="Deluxe Wagyu Steakhouse Burger",
                category="Burger",
                base_price=Decimal("5.99"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['deluxe wagyu steakhouse', 'steakhouse', 'wagyu steakhouse', 'wagyu steakhouse burger', 'deluxe wagyu', 'deluxe', 'steakhouse burger', 'wagyu', 'burger']
            ),
            MenuItemTemplate(
                name="Bacon Ranch Wagyu Steakhouse Burger",
                category="Burger",
                base_price=Decimal("6.99"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['bacon', 'extra sauce', 'no onions', 'cheese', 'extra cheese', 'no pickles'],
                modification_pricing={
                "bacon": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['ranch wagyu steakhouse burger', 'ranch wagyu steakhouse', 'bacon ranch', 'bacon', 'bacon ranch wagyu', 'steakhouse', 'bacon ranch wagyu steakhouse', 'ranch wagyu', 'wagyu steakhouse', 'wagyu steakhouse burger', 'steakhouse burger', 'wagyu', 'ranch', 'burger']
            ),
            MenuItemTemplate(
                name="Chicken Cheddar Ranch",
                category="Main Dish",
                base_price=Decimal("5.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['cheddar', 'chicken', 'chicken cheddar', 'cheddar ranch', 'ranch']
            ),
            MenuItemTemplate(
                name="Pecan Chicken Salad",
                category="Main Dish",
                base_price=Decimal("6.69"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['pecan', 'chicken', 'chicken salad', 'salad', 'pecan chicken']
            ),
            MenuItemTemplate(
                name="White Cheddar Mac 'n Cheese",
                category="Main Dish",
                base_price=Decimal("3.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=["cheddar mac 'n cheese", "cheddar mac 'n", "'n", 'white cheddar', 'cheddar', "'n cheese", "mac 'n", 'cheese', "white cheddar mac 'n", 'cheddar mac', "mac 'n cheese", 'mac', 'white', 'white cheddar mac']
            ),
            MenuItemTemplate(
                name="Orange Cream Shake",
                category="Main Dish",
                base_price=Decimal("3.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['shake', 'cream', 'cream shake', 'orange cream', 'orange']
            ),
            MenuItemTemplate(
                name="Mozzarella Sticks (6 ea.)",
                category="Main Dish",
                base_price=Decimal("5.89"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['sticks (6', 'ea.)', 'sticks', 'mozzarella sticks (6', '(6 ea.)', 'mozzarella sticks', 'sticks (6 ea.)', 'mozzarella', '(6']
            ),
            MenuItemTemplate(
                name="Smokehouse Brisket",
                category="Main Dish",
                base_price=Decimal("7.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['brisket', 'smokehouse']
            ),
            MenuItemTemplate(
                name="Double Beef 'n Cheddar",
                category="Main Dish",
                base_price=Decimal("7.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=["'n", 'beef', 'cheddar', 'double beef', 'double', "beef 'n cheddar", "beef 'n", "'n cheddar", "double beef 'n"]
            ),
            MenuItemTemplate(
                name="Roast Turkey Ranch &amp; Bacon Sandwich",
                category="Salad",
                base_price=Decimal("6.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon', 'extra sauce', 'no onions', 'cheese', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "bacon": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['turkey ranch', 'turkey ranch &amp; bacon', 'bacon', 'turkey ranch &amp; bacon sandwich', 'roast turkey ranch', 'bacon sandwich', 'sandwich', 'roast turkey', '&amp; bacon sandwich', 'roast turkey ranch &amp;', '&amp; bacon', 'turkey', 'ranch &amp;', 'ranch &amp; bacon', 'turkey ranch &amp;', 'roast turkey ranch &amp; bacon', 'roast', 'ranch &amp; bacon sandwich', '&amp;', 'ranch']
            ),
            MenuItemTemplate(
                name="Italian B.M.T.® Footlong Pro (Double Protein)",
                category="Pizza",
                base_price=Decimal("12.49"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['italian b.m.t.® footlong pro', 'italian', 'pro (double protein)', 'b.m.t.® footlong pro (double protein)', 'footlong pro (double protein)', 'italian b.m.t.® footlong pro (double', 'b.m.t.® footlong pro', '(double', 'b.m.t.®', 'footlong pro (double', '(double protein)', 'protein)', 'footlong pro', 'pro (double', 'italian b.m.t.®', 'b.m.t.® footlong pro (double', 'pro', 'b.m.t.® footlong', 'italian b.m.t.® footlong', 'footlong']
            ),
            MenuItemTemplate(
                name="Steak &amp; Cheese Footlong Regular Sub",
                category="Beverage",
                base_price=Decimal("9.99"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['steak', 'cheese footlong', 'steak &amp; cheese footlong regular', 'cheese', 'footlong regular', 'cheese footlong regular sub', 'steak &amp;', '&amp; cheese footlong regular sub', 'cheese footlong regular', 'steak &amp; cheese footlong', 'footlong regular sub', 'steak &amp; cheese', '&amp; cheese footlong', '&amp; cheese footlong regular', 'sub', 'regular', 'regular sub', 'footlong', '&amp;', '&amp; cheese']
            ),
            MenuItemTemplate(
                name="Tuna Footlong Regular Sub",
                category="Sandwich",
                base_price=Decimal("9.49"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['sub', 'regular', 'footlong regular sub', 'tuna', 'tuna footlong regular', 'footlong regular', 'regular sub', 'tuna footlong', 'footlong']
            ),
            MenuItemTemplate(
                name="Steak, Egg &amp; Cheese Footlong with Regular Egg",
                category="Beverage",
                base_price=Decimal("7.49"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['egg &amp; cheese footlong with regular', 'cheese footlong', 'with', 'cheese', 'steak, egg &amp; cheese footlong with', 'cheese footlong with regular', 'steak, egg &amp; cheese footlong with regular', 'steak, egg &amp; cheese', 'egg &amp; cheese footlong with', 'steak, egg &amp;', 'steak, egg &amp; cheese footlong', 'footlong with regular', 'regular egg', 'egg &amp;', 'footlong with', '&amp; cheese footlong with regular', '&amp; cheese footlong with regular egg', 'egg', 'footlong with regular egg', 'egg &amp; cheese footlong with regular egg', 'egg &amp; cheese', 'steak,', '&amp; cheese footlong', 'steak, egg', 'cheese footlong with regular egg', 'egg &amp; cheese footlong', 'regular', '&amp; cheese footlong with', 'with regular egg', 'with regular', 'cheese footlong with', 'footlong', '&amp;', '&amp; cheese']
            ),
            MenuItemTemplate(
                name="Baja Turkey Avocado Footlong Pro (Double Protein)",
                category="Main Dish",
                base_price=Decimal("14.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['turkey avocado', 'avocado footlong', 'avocado footlong pro (double', 'turkey avocado footlong', 'pro (double protein)', 'turkey avocado footlong pro', 'footlong pro (double protein)', 'avocado', '(double', 'baja turkey avocado footlong', 'baja turkey avocado footlong pro', 'footlong pro (double', 'turkey avocado footlong pro (double', 'protein)', 'baja turkey avocado footlong pro (double', 'turkey', '(double protein)', 'avocado footlong pro', 'baja turkey avocado', 'footlong pro', 'baja', 'pro (double', 'turkey avocado footlong pro (double protein)', 'avocado footlong pro (double protein)', 'baja turkey', 'pro', 'footlong']
            ),
            MenuItemTemplate(
                name="Sweet Onion Steak Teriyaki 6 Inch Regular Sub",
                category="Beverage",
                base_price=Decimal("6.99"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['sweet onion', 'steak', 'sweet onion steak', 'inch regular sub', 'teriyaki 6 inch regular sub', '6 inch regular', 'inch', 'steak teriyaki 6 inch regular', 'steak teriyaki', 'onion steak teriyaki', '6', 'teriyaki 6 inch regular', 'sweet onion steak teriyaki 6 inch regular', 'onion steak teriyaki 6 inch', 'teriyaki 6 inch', 'steak teriyaki 6', 'sweet onion steak teriyaki 6 inch', 'onion steak teriyaki 6 inch regular', '6 inch', 'onion', 'sweet onion steak teriyaki 6', 'steak teriyaki 6 inch regular sub', 'sweet onion steak teriyaki', '6 inch regular sub', 'teriyaki 6', 'teriyaki', 'steak teriyaki 6 inch', 'inch regular', 'sweet', 'sub', 'onion steak teriyaki 6', 'regular', 'onion steak', 'onion steak teriyaki 6 inch regular sub', 'regular sub']
            ),
            MenuItemTemplate(
                name="Sweet Onion Steak Teriyaki Footlong Regular Sub",
                category="Beverage",
                base_price=Decimal("10.99"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['sweet onion', 'steak', 'sweet onion steak', 'footlong regular', 'steak teriyaki', 'onion steak teriyaki', 'onion steak teriyaki footlong', 'steak teriyaki footlong regular', 'steak teriyaki footlong', 'teriyaki footlong regular sub', 'teriyaki footlong', 'sweet onion steak teriyaki footlong', 'sweet onion steak teriyaki footlong regular', 'onion', 'footlong regular sub', 'sweet onion steak teriyaki', 'steak teriyaki footlong regular sub', 'teriyaki', 'teriyaki footlong regular', 'sweet', 'sub', 'regular', 'onion steak', 'onion steak teriyaki footlong regular sub', 'onion steak teriyaki footlong regular', 'regular sub', 'footlong']
            ),
            MenuItemTemplate(
                name="Sweet Onion Steak Teriyaki Footlong Pro (Double Protein)",
                category="Beverage",
                base_price=Decimal("14.49"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['sweet onion', 'steak', 'sweet onion steak', 'steak teriyaki footlong pro (double protein)', 'teriyaki footlong pro (double', 'steak teriyaki', 'sweet onion steak teriyaki footlong pro (double', 'onion steak teriyaki', 'onion steak teriyaki footlong', 'pro (double protein)', 'footlong pro (double protein)', 'steak teriyaki footlong', 'teriyaki footlong', 'sweet onion steak teriyaki footlong', 'onion', '(double', 'teriyaki footlong pro', 'steak teriyaki footlong pro', 'sweet onion steak teriyaki', 'footlong pro (double', '(double protein)', 'protein)', 'teriyaki', 'steak teriyaki footlong pro (double', 'pro', 'footlong pro', 'sweet', 'pro (double', 'onion steak', 'teriyaki footlong pro (double protein)', 'onion steak teriyaki footlong pro (double protein)', 'onion steak teriyaki footlong pro', 'onion steak teriyaki footlong pro (double', 'sweet onion steak teriyaki footlong pro', 'footlong']
            ),
            MenuItemTemplate(
                name="Sweet Onion Chicken Teriyaki 6 Inch Regular Sub",
                category="Main Dish",
                base_price=Decimal("6.49"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['sweet onion', 'chicken teriyaki 6 inch regular', 'inch regular sub', 'teriyaki 6 inch regular sub', '6 inch regular', 'inch', '6', 'teriyaki 6 inch regular', 'teriyaki 6 inch', 'chicken teriyaki 6 inch', 'sweet onion chicken', 'onion chicken teriyaki', 'chicken', 'onion chicken teriyaki 6 inch regular sub', 'chicken teriyaki 6', '6 inch', 'onion', 'chicken teriyaki', 'sweet onion chicken teriyaki 6 inch', 'sweet onion chicken teriyaki 6 inch regular', 'onion chicken', '6 inch regular sub', 'teriyaki 6', 'teriyaki', 'onion chicken teriyaki 6', 'inch regular', 'chicken teriyaki 6 inch regular sub', 'sweet', 'sub', 'regular', 'onion chicken teriyaki 6 inch', 'regular sub', 'onion chicken teriyaki 6 inch regular', 'sweet onion chicken teriyaki 6', 'sweet onion chicken teriyaki']
            ),
            MenuItemTemplate(
                name="Sweet Onion Chicken Teriyaki Footlong Regular Sub",
                category="Main Dish",
                base_price=Decimal("9.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['chicken teriyaki footlong regular', 'sweet onion', 'sweet onion chicken teriyaki footlong', 'footlong regular', 'chicken teriyaki footlong', 'sweet onion chicken', 'onion chicken teriyaki', 'teriyaki footlong regular sub', 'chicken', 'teriyaki footlong', 'onion', 'sweet onion chicken teriyaki footlong regular', 'onion chicken teriyaki footlong', 'onion chicken teriyaki footlong regular sub', 'chicken teriyaki', 'footlong regular sub', 'onion chicken', 'teriyaki', 'teriyaki footlong regular', 'onion chicken teriyaki footlong regular', 'sweet', 'sub', 'regular', 'chicken teriyaki footlong regular sub', 'regular sub', 'footlong', 'sweet onion chicken teriyaki']
            ),
            MenuItemTemplate(
                name="Sweet Onion Chicken Teriyaki Footlong Pro (Double Protein)",
                category="Main Dish",
                base_price=Decimal("13.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['sweet onion', 'onion chicken teriyaki footlong pro (double protein)', 'chicken teriyaki footlong pro', 'sweet onion chicken teriyaki footlong', 'teriyaki footlong pro (double', 'onion chicken teriyaki footlong pro', 'pro (double protein)', 'chicken teriyaki footlong', 'sweet onion chicken', 'footlong pro (double protein)', 'onion chicken teriyaki', 'chicken', 'teriyaki footlong', 'onion', '(double', 'onion chicken teriyaki footlong', 'chicken teriyaki', 'teriyaki footlong pro', 'onion chicken', 'footlong pro (double', 'onion chicken teriyaki footlong pro (double', 'protein)', 'teriyaki', 'chicken teriyaki footlong pro (double protein)', '(double protein)', 'sweet onion chicken teriyaki footlong pro (double', 'footlong pro', 'sweet', 'chicken teriyaki footlong pro (double', 'pro (double', 'teriyaki footlong pro (double protein)', 'sweet onion chicken teriyaki footlong pro', 'pro', 'footlong', 'sweet onion chicken teriyaki']
            ),
            MenuItemTemplate(
                name="Mozza Meat  6 Inch Regular Sub",
                category="Sandwich",
                base_price=Decimal("6.49"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['regular sub', 'inch regular sub', '6 inch regular', 'inch', '6', 'meat 6', 'meat 6 inch regular', '6 inch', 'mozza meat 6 inch regular', 'meat 6 inch regular sub', 'mozza', '6 inch regular sub', 'mozza meat', 'meat', 'mozza meat 6', 'inch regular', 'meat 6 inch', 'sub', 'regular', 'mozza meat 6 inch', 'mozza meat 6 inch regular sub']
            ),
            MenuItemTemplate(
                name="Mozza Meat  Footlong Regular Sub",
                category="Sandwich",
                base_price=Decimal("10.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['meat footlong', 'sub', 'mozza', 'regular', 'mozza meat footlong', 'mozza meat', 'meat', 'footlong regular sub', 'footlong regular', 'meat footlong regular', 'meat footlong regular sub', 'mozza meat footlong regular', 'regular sub', 'mozza meat footlong regular sub', 'footlong']
            ),
            MenuItemTemplate(
                name="Mozza Meat  Footlong Pro (Double Protein)",
                category="Sandwich",
                base_price=Decimal("14.49"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['meat footlong pro (double', 'meat footlong pro (double protein)', 'mozza meat footlong pro', 'pro (double protein)', 'footlong pro (double protein)', 'meat footlong', '(double', 'mozza', 'mozza meat footlong', 'mozza meat', 'meat', 'mozza meat footlong pro (double protein)', 'footlong pro (double', 'protein)', '(double protein)', 'meat footlong pro', 'footlong pro', 'mozza meat footlong pro (double', 'pro (double', 'pro', 'footlong']
            ),
            MenuItemTemplate(
                name="Supreme Meats 6 Inch Regular Sub",
                category="Pizza",
                base_price=Decimal("6.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['inch regular sub', '6 inch regular', 'inch', 'supreme meats', 'meats 6 inch regular', 'supreme meats 6', '6', '6 inch', 'meats 6 inch', '6 inch regular sub', 'inch regular', 'sub', 'supreme meats 6 inch', 'meats 6 inch regular sub', 'regular', 'meats', 'supreme', 'supreme meats 6 inch regular', 'meats 6', 'regular sub']
            ),
            MenuItemTemplate(
                name="Buffalo Ranch Sandwich",
                category="Sandwich",
                base_price=Decimal("5.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['buffalo', 'ranch sandwich', 'buffalo ranch', 'sandwich', 'ranch']
            ),
            MenuItemTemplate(
                name="4 Sandwich Family Feast",
                category="Sandwich",
                base_price=Decimal("20.89"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['4 sandwich', 'feast', '4', 'sandwich family feast', 'sandwich family', '4 sandwich family', 'family', 'family feast', 'sandwich']
            ),
            MenuItemTemplate(
                name="Mixed Chicken Family Meal (8 Pcs)",
                category="Main Dish",
                base_price=Decimal("23.6"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['mixed chicken family', 'chicken family', 'mixed chicken family meal (8', '(8 pcs)', 'meal', 'meal (8', 'chicken family meal', 'chicken', 'family', 'pcs)', 'family meal (8', '(8', 'chicken family meal (8 pcs)', 'chicken family meal (8', 'mixed chicken', 'family meal (8 pcs)', 'family meal', 'mixed', 'meal (8 pcs)', 'mixed chicken family meal']
            ),
            MenuItemTemplate(
                name="Chicken Combo (3 Pcs)",
                category="Beverage",
                base_price=Decimal("9.89"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['combo (3', 'combo (3 pcs)', '(3', 'chicken', 'chicken combo (3', '(3 pcs)', 'pcs)', 'combo', 'chicken combo']
            ),
            MenuItemTemplate(
                name="Surf &amp; Turf Combo",
                category="Beverage",
                base_price=Decimal("8.4"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['surf &amp;', 'turf combo', '&amp; turf', '&amp; turf combo', 'surf &amp; turf', 'combo', 'turf', '&amp;', 'surf']
            ),
            MenuItemTemplate(
                name="Buffalo Ranch Sandwich Dinner",
                category="Sandwich",
                base_price=Decimal("7.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['buffalo', 'ranch sandwich dinner', 'dinner', 'ranch sandwich', 'buffalo ranch', 'sandwich dinner', 'buffalo ranch sandwich', 'sandwich', 'ranch']
            ),
            MenuItemTemplate(
                name="Buffalo Ranch Sandwich Combo",
                category="Beverage",
                base_price=Decimal("8.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['buffalo', 'ranch sandwich combo', 'ranch sandwich', 'buffalo ranch', 'combo', 'sandwich combo', 'buffalo ranch sandwich', 'sandwich', 'ranch']
            ),
            MenuItemTemplate(
                name="Classic Chicken Sandwich",
                category="Main Dish",
                base_price=Decimal("5.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sand', 'classic chicken', 'chicken sandwich', 'chick sandwich', 'chicken', 'classic', 'sandwich']
            ),
            MenuItemTemplate(
                name="Spicy Chicken Sandwich",
                category="Main Dish",
                base_price=Decimal("5.19"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sand', 'chicken sandwich', 'chick sandwich', 'chicken', 'spicy', 'spicy chicken', 'sandwich']
            ),
            MenuItemTemplate(
                name="Classic Chicken Sandwich Combo",
                category="Beverage",
                base_price=Decimal("8.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sand', 'classic chicken', 'classic chicken sandwich', 'chicken sandwich', 'chick sandwich', 'chicken', 'chicken sandwich combo', 'classic', 'combo', 'sandwich combo', 'sandwich']
            ),
            MenuItemTemplate(
                name="Spicy Chicken Sandwich Combo",
                category="Beverage",
                base_price=Decimal("8.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sand', 'chicken sandwich', 'chick sandwich', 'chicken', 'chicken sandwich combo', 'spicy', 'spicy chicken sandwich', 'combo', 'sandwich combo', 'spicy chicken', 'sandwich']
            ),
            MenuItemTemplate(
                name="Classic Chicken Sandwich Dinner",
                category="Main Dish",
                base_price=Decimal("8.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sand', 'classic chicken', 'classic chicken sandwich', 'chicken sandwich', 'chick sandwich', 'chicken', 'dinner', 'classic', 'sandwich dinner', 'sandwich', 'chicken sandwich dinner']
            ),
            MenuItemTemplate(
                name="Spicy Chicken Sandwich Dinner",
                category="Main Dish",
                base_price=Decimal("8.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['no pickles', 'extra cheese', 'extra sauce', 'no onions'],
                modification_pricing={
                "no pickles": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
            },
                keywords=['chicken sand', 'chicken sandwich', 'chick sandwich', 'chicken', 'spicy', 'dinner', 'spicy chicken sandwich', 'sandwich dinner', 'spicy chicken', 'sandwich', 'chicken sandwich dinner']
            ),
            MenuItemTemplate(
                name="BIg Family Feast",
                category="Main Dish",
                base_price=Decimal("36.29"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['big', 'feast', 'family', 'big family', 'family feast']
            ),
            MenuItemTemplate(
                name="Bigger Family Feast",
                category="Main Dish",
                base_price=Decimal("60.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['feast', 'bigger', 'family', 'bigger family', 'family feast']
            ),
            MenuItemTemplate(
                name="Large Cheese",
                category="Main Dish",
                base_price=Decimal("15.35"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['cheese', 'large']
            ),
            MenuItemTemplate(
                name="Large Meat Lovers",
                category="Pizza",
                base_price=Decimal("21.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon'],
                modification_pricing={
                "bacon": Decimal("0.00"),
            },
                keywords=['meat lovers', 'large', 'lovers', 'large meat', 'meat']
            ),
            MenuItemTemplate(
                name="Cheese Sticks",
                category="Main Dish",
                base_price=Decimal("7.43"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['cheese', 'sticks']
            ),
            MenuItemTemplate(
                name="Medium Cheese",
                category="Main Dish",
                base_price=Decimal("12.95"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['cheese', 'medium']
            ),
            MenuItemTemplate(
                name="Cinnamon Sticks",
                category="Pizza",
                base_price=Decimal("6.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['sticks', 'cinnamon']
            ),
            MenuItemTemplate(
                name="Large Hawaiian Chicken",
                category="Pizza",
                base_price=Decimal("21.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['large hawaiian', 'large', 'hawaiian chicken', 'chicken', 'hawaiian']
            ),
            MenuItemTemplate(
                name="Large Supreme",
                category="Pizza",
                base_price=Decimal("21.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['supreme', 'large']
            ),
            MenuItemTemplate(
                name="Large Pep Lovers",
                category="Pizza",
                base_price=Decimal("21.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['pep', 'pep lovers', 'lovers', 'large', 'large pep']
            ),
            MenuItemTemplate(
                name="Large Buffalo Chicken",
                category="Main Dish",
                base_price=Decimal("21.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['sauce'],
                modification_pricing={
                "sauce": Decimal("0.00"),
            },
                keywords=['large', 'buffalo chicken', 'buffalo', 'chicken', 'large buffalo']
            ),
            MenuItemTemplate(
                name="Large Veg Lovers",
                category="Main Dish",
                base_price=Decimal("21.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['large', 'lovers', 'large veg', 'veg lovers', 'veg']
            ),
            MenuItemTemplate(
                name="Large Sup Supreme",
                category="Pizza",
                base_price=Decimal("22.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['large sup', 'large', 'sup supreme', 'supreme', 'sup']
            ),
            MenuItemTemplate(
                name="Large Hawaiian Luau",
                category="Dessert",
                base_price=Decimal("21.59"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon'],
                modification_pricing={
                "bacon": Decimal("0.00"),
            },
                keywords=['large hawaiian', 'large', 'luau', 'hawaiian', 'hawaiian luau']
            ),
            MenuItemTemplate(
                name="Medium Hawaiian Chicken",
                category="Pizza",
                base_price=Decimal("18.47"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['medium hawaiian', 'hawaiian chicken', 'medium', 'chicken', 'hawaiian']
            ),
            MenuItemTemplate(
                name="Medium Supreme",
                category="Pizza",
                base_price=Decimal("18.47"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['supreme', 'medium']
            ),
            MenuItemTemplate(
                name="Medium Meat Lovers",
                category="Pizza",
                base_price=Decimal("18.47"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon'],
                modification_pricing={
                "bacon": Decimal("0.00"),
            },
                keywords=['meat lovers', 'lovers', 'medium', 'meat', 'medium meat']
            ),
            MenuItemTemplate(
                name="SONIC® Cheeseburger",
                category="Burger",
                base_price=Decimal("5.72"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['cheese burger', 'cheesburger', 'sonic®', 'cheeseburger']
            ),
            MenuItemTemplate(
                name="Footlong Quarter Pound Coney",
                category="Main Dish",
                base_price=Decimal("5.6"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['footlong quarter pound', 'pound', 'pound coney', 'coney', 'quarter pound coney', 'quarter pound', 'footlong', 'quarter', 'footlong quarter']
            ),
            MenuItemTemplate(
                name="SuperSONIC® Breakfast Burrito",
                category="Sandwich",
                base_price=Decimal("5.36"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['breakfast burrito', 'breakfast', 'burito', 'supersonic®', 'supersonic® breakfast', 'burrito']
            ),
            MenuItemTemplate(
                name="Corn Dog",
                category="Main Dish",
                base_price=Decimal("1.94"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['corn', 'dog']
            ),
            MenuItemTemplate(
                name="Soft Pretzel Twist",
                category="Main Dish",
                base_price=Decimal("2.43"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['pretzel twist', 'soft pretzel', 'pretzel', 'twist', 'soft']
            ),
            MenuItemTemplate(
                name="Cake Batter Shake",
                category="Dessert",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['cake batter', 'shake', 'batter shake', 'cake', 'batter']
            ),
            MenuItemTemplate(
                name="Brownie Batter Master Shake®",
                category="Dessert",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['shake®', 'batter master shake®', 'brownie', 'batter', 'brownie batter master', 'master shake®', 'batter master', 'master', 'brownie batter']
            ),
            MenuItemTemplate(
                name="Red Bull® Slush",
                category="Beverage",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['bull®', 'slush', 'bull® slush', 'red bull®', 'red']
            ),
            MenuItemTemplate(
                name="Strawberry Apricot Red Bull® Slush",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['strawberry', 'bull®', 'slush', 'strawberry apricot red', 'red bull® slush', 'apricot', 'apricot red', 'bull® slush', 'red bull®', 'strawberry apricot', 'strawberry apricot red bull®', 'apricot red bull®', 'red', 'apricot red bull® slush']
            ),
            MenuItemTemplate(
                name="Red Bull® Energy Drink",
                category="Beverage",
                base_price=Decimal("3.65"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['bull® energy', 'bull®', 'energy', 'red bull® energy', 'bull® energy drink', 'red bull®', 'drink', 'red', 'energy drink']
            ),
            MenuItemTemplate(
                name="Strawberry Apricot Red Bull® Energy Drink",
                category="Beverage",
                base_price=Decimal("3.65"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['red bull® energy', 'apricot red', 'apricot red bull® energy', 'red', 'energy drink', 'drink', 'strawberry apricot', 'strawberry apricot red', 'strawberry apricot red bull® energy', 'red bull® energy drink', 'bull®', 'energy', 'apricot', 'strawberry apricot red bull®', 'red bull®', 'strawberry', 'apricot red bull® energy drink', 'bull® energy', 'bull® energy drink', 'apricot red bull®']
            ),
            MenuItemTemplate(
                name="The Big Dill Cheeseburger",
                category="Burger",
                base_price=Decimal("6.21"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['cheesburger', 'big', 'the', 'dill', 'the big', 'cheese burger', 'the big dill', 'big dill cheeseburger', 'big dill', 'dill cheeseburger', 'cheeseburger']
            ),
            MenuItemTemplate(
                name="SONIC® Cheeseburger Combo",
                category="Burger",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['cheesburger', 'cheeseburger combo', 'sonic® cheeseburger', 'sonic®', 'cheese burger', 'combo', 'cheeseburger']
            ),
            MenuItemTemplate(
                name="SuperSONIC® Double Cheeseburger Combo",
                category="Burger",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['cheesburger', 'cheeseburger combo', 'double cheeseburger', 'supersonic® double', 'supersonic® double cheeseburger', 'cheese burger', 'double', 'supersonic®', 'combo', 'double cheeseburger combo', 'cheeseburger']
            ),
            MenuItemTemplate(
                name="SuperSONIC® Bacon Double Cheeseburger Combo",
                category="Burger",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon', 'extra sauce', 'no onions', 'cheese', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "bacon": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['cheesburger', 'supersonic® bacon double cheeseburger', 'bacon', 'double cheeseburger', 'bacon double', 'double cheeseburger combo', 'cheeseburger combo', 'supersonic® bacon', 'bacon double cheeseburger', 'cheese burger', 'double', 'supersonic® bacon double', 'supersonic®', 'combo', 'bacon double cheeseburger combo', 'cheeseburger']
            ),
            MenuItemTemplate(
                name="Burrito Bowl",
                category="Main Dish",
                base_price=Decimal("10.15"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['burito', 'burrito', 'bowl']
            ),
            MenuItemTemplate(
                name="Burrito",
                category="Sandwich",
                base_price=Decimal("10.15"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['burito']
            ),
            MenuItemTemplate(
                name="Chips &amp; Queso Blanco",
                category="Main Dish",
                base_price=Decimal("5.3"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['queso blanco', 'queso', 'chips &amp;', '&amp; queso', 'chips &amp; queso', 'chips', 'blanco', '&amp; queso blanco', '&amp;']
            ),
            MenuItemTemplate(
                name="Quesadilla",
                category="Main Dish",
                base_price=Decimal("10.85"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['quesadila', 'quesa']
            ),
            MenuItemTemplate(
                name="Mexican Coca-Cola",
                category="Main Dish",
                base_price=Decimal("3.65"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['coca-cola', 'mexican']
            ),
            MenuItemTemplate(
                name="Salad",
                category="Salad",
                base_price=Decimal("10.15"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=[]
            ),
            MenuItemTemplate(
                name="Three Tacos",
                category="Main Dish",
                base_price=Decimal("10.15"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['three', 'tacos']
            ),
            MenuItemTemplate(
                name="Tacos",
                category="Salad",
                base_price=Decimal("3.7"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=[]
            ),
            MenuItemTemplate(
                name="Kid's Build Your Own",
                category="Main Dish",
                base_price=Decimal("6.45"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['your', 'own', 'your own', "kid's", "kid's build your", 'build your own', 'build', 'build your', "kid's build"]
            ),
            MenuItemTemplate(
                name="Kid's Quesadilla",
                category="Main Dish",
                base_price=Decimal("5.1"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['quesadila', "kid's", 'quesadilla', 'quesa']
            ),
            MenuItemTemplate(
                name="Whole30® Salad Bowl",
                category="Main Dish",
                base_price=Decimal("13.3"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['bowl', 'salad bowl', 'whole30®', 'salad', 'whole30® salad']
            ),
            MenuItemTemplate(
                name="Keto Salad Bowl",
                category="Main Dish",
                base_price=Decimal("13.3"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['bowl', 'keto', 'keto salad', 'salad bowl', 'salad']
            ),
            MenuItemTemplate(
                name="High Protein Bowl",
                category="Beverage",
                base_price=Decimal("15.75"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['protein bowl', 'high', 'bowl', 'protein', 'high protein']
            ),
            MenuItemTemplate(
                name="Paleo Salad Bowl",
                category="Main Dish",
                base_price=Decimal("13.3"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['bowl', 'paleo salad', 'salad bowl', 'paleo', 'salad']
            ),
            MenuItemTemplate(
                name="Vegetarian Salad Bowl",
                category="Salad",
                base_price=Decimal("10.15"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['vegetarian', 'bowl', 'vegetarian salad', 'salad bowl', 'salad']
            ),
            MenuItemTemplate(
                name="Latte",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['extra foam', 'extra shot', 'extra hot', 'decaf'],
                modification_pricing={
                "extra foam": Decimal("0.50"),
                "extra shot": Decimal("0.50"),
                "extra hot": Decimal("0.50"),
                "decaf": Decimal("0.00"),
            },
                keywords=[]
            ),
            MenuItemTemplate(
                name="Iced Latte",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['extra foam', 'extra shot', 'extra hot', 'decaf'],
                modification_pricing={
                "extra foam": Decimal("0.50"),
                "extra shot": Decimal("0.50"),
                "extra hot": Decimal("0.50"),
                "decaf": Decimal("0.00"),
            },
                keywords=['iced', 'latte']
            ),
            MenuItemTemplate(
                name="Cappuccino",
                category="Beverage",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['capp']
            ),
            MenuItemTemplate(
                name="Iced Cappuccino",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['iced', 'capp', 'cappuccino']
            ),
            MenuItemTemplate(
                name="Macchiato",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['mach']
            ),
            MenuItemTemplate(
                name="Iced Macchiato",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['iced', 'mach', 'macchiato']
            ),
            MenuItemTemplate(
                name="Americano",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['american coffee']
            ),
            MenuItemTemplate(
                name="Iced Americano",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['iced', 'american coffee', 'americano']
            ),
            MenuItemTemplate(
                name="Shot of Espresso",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['shot', 'espresso', 'of', 'of espresso', 'shot of']
            ),
            MenuItemTemplate(
                name="Sunrise Batch Iced Coffee",
                category="Beverage",
                base_price=Decimal("0.0"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['extra foam', 'extra shot', 'extra hot', 'decaf'],
                modification_pricing={
                "extra foam": Decimal("0.50"),
                "extra shot": Decimal("0.50"),
                "extra hot": Decimal("0.50"),
                "decaf": Decimal("0.00"),
            },
                keywords=['coffee', 'sunrise', 'sunrise batch', 'batch iced', 'iced', 'sunrise batch iced', 'iced coffee', 'batch iced coffee', 'batch']
            ),
            MenuItemTemplate(
                name="Original Blend Iced Coffee",
                category="Beverage",
                base_price=Decimal("0.0"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['extra foam', 'extra shot', 'extra hot', 'decaf'],
                modification_pricing={
                "extra foam": Decimal("0.50"),
                "extra shot": Decimal("0.50"),
                "extra hot": Decimal("0.50"),
                "decaf": Decimal("0.00"),
            },
                keywords=['blend iced', 'original', 'blend', 'coffee', 'iced', 'blend iced coffee', 'original blend', 'iced coffee', 'original blend iced']
            ),
            MenuItemTemplate(
                name="Cold Brew",
                category="Beverage",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['brew', 'cold']
            ),
            MenuItemTemplate(
                name="Iced Chai Latte",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['extra foam', 'extra shot', 'extra hot', 'decaf'],
                modification_pricing={
                "extra foam": Decimal("0.50"),
                "extra shot": Decimal("0.50"),
                "extra hot": Decimal("0.50"),
                "decaf": Decimal("0.00"),
            },
                keywords=['iced', 'iced chai', 'chai', 'latte', 'chai latte']
            ),
            MenuItemTemplate(
                name="Iced Matcha Latte",
                category="Beverage",
                base_price=Decimal("0.0"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['extra foam', 'extra shot', 'extra hot', 'decaf'],
                modification_pricing={
                "extra foam": Decimal("0.50"),
                "extra shot": Decimal("0.50"),
                "extra hot": Decimal("0.50"),
                "decaf": Decimal("0.00"),
            },
                keywords=['matcha latte', 'iced', 'iced matcha', 'latte', 'matcha']
            ),
            MenuItemTemplate(
                name="Iced Tea",
                category="Beverage",
                base_price=Decimal("0.0"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['iced', 'tea', 'ice tea']
            ),
            MenuItemTemplate(
                name="Plate",
                category="Main Dish",
                base_price=Decimal("11.25"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=[]
            ),
            MenuItemTemplate(
                name="Bigger Plate",
                category="Main Dish",
                base_price=Decimal("13.15"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['plate', 'bigger']
            ),
            MenuItemTemplate(
                name="Sprite",
                category="Beverage",
                base_price=Decimal("2.65"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=[]
            ),
            MenuItemTemplate(
                name="Bowl",
                category="Main Dish",
                base_price=Decimal("9.4"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=[]
            ),
            MenuItemTemplate(
                name="Dr Pepper",
                category="Main Dish",
                base_price=Decimal("2.65"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['dr', 'pepper']
            ),
            MenuItemTemplate(
                name="Family Meal",
                category="Main Dish",
                base_price=Decimal("40.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['family', 'meal']
            ),
            MenuItemTemplate(
                name="Orange Chicken Cub Meal",
                category="Main Dish",
                base_price=Decimal("7.75"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['orange chicken cub', 'chicken cub', 'orange chicken', 'chicken', 'chicken cub meal', 'cub', 'meal', 'orange', 'cub meal']
            ),
            MenuItemTemplate(
                name="Grilled Teriyaki Chicken Cub Meal",
                category="Main Dish",
                base_price=Decimal("7.75"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['grilled teriyaki chicken cub', 'grilled teriyaki', 'grilled teriyaki chicken', 'chicken cub', 'teriyaki chicken cub', 'chicken', 'chicken cub meal', 'cub', 'teriyaki', 'meal', 'teriyaki chicken cub meal', 'teriyaki chicken', 'cub meal', 'grilled']
            ),
            MenuItemTemplate(
                name="Broccoli Beef Cub Meal",
                category="Salad",
                base_price=Decimal("7.75"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['broccoli', 'beef cub meal', 'beef', 'broccoli beef', 'cub', 'meal', 'beef cub', 'broccoli beef cub', 'cub meal']
            ),
            MenuItemTemplate(
                name="Wok-Fired Shrimp",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['wok-fired', 'shrimp']
            ),
            MenuItemTemplate(
                name="The Original Orange Chicken",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['original orange', 'original', 'the original', 'the', 'the original orange', 'orange chicken', 'chicken', 'original orange chicken', 'orange']
            ),
            MenuItemTemplate(
                name="Black Pepper Angus Steak",
                category="Beverage",
                base_price=Decimal("0.0"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['steak', 'black pepper angus', 'angus', 'black pepper', 'black', 'angus steak', 'pepper angus steak', 'pepper', 'pepper angus']
            ),
            MenuItemTemplate(
                name="Honey Walnut Shrimp",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['shrimp', 'honey', 'walnut', 'walnut shrimp', 'honey walnut']
            ),
            MenuItemTemplate(
                name="Grilled Teriyaki Chicken",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['grilled teriyaki', 'chicken', 'teriyaki', 'teriyaki chicken', 'grilled']
            ),
            MenuItemTemplate(
                name="Broccoli Beef",
                category="Main Dish",
                base_price=Decimal("0.0"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['broccoli', 'beef']
            ),
            MenuItemTemplate(
                name="Create Your Own",
                category="Main Dish",
                base_price=Decimal("9.49"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['your', 'create', 'own', 'your own', 'create your']
            ),
            MenuItemTemplate(
                name="Tuscan Six Cheese",
                category="Main Dish",
                base_price=Decimal("13.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['six', 'tuscan', 'tuscan six', 'cheese', 'six cheese']
            ),
            MenuItemTemplate(
                name="Fresh Spinach &amp; Tomato Alfredo",
                category="Main Dish",
                base_price=Decimal("13.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['tomato alfredo', 'spinach &amp;', 'fresh spinach &amp; tomato', 'alfredo', '&amp; tomato', 'fresh', 'spinach &amp; tomato', '&amp; tomato alfredo', 'spinach &amp; tomato alfredo', 'fresh spinach', 'tomato', '&amp;', 'fresh spinach &amp;', 'spinach']
            ),
            MenuItemTemplate(
                name="The Works",
                category="Main Dish",
                base_price=Decimal("13.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['the', 'works']
            ),
            MenuItemTemplate(
                name="Pepperoni",
                category="Pizza",
                base_price=Decimal("10.98"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=[]
            ),
            MenuItemTemplate(
                name="Spicy Pepperoni Rolls",
                category="Pizza",
                base_price=Decimal("6.49"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['pepperoni rolls', 'spicy pepperoni', 'rolls', 'spicy', 'pepperoni']
            ),
            MenuItemTemplate(
                name="Epic Pepperoni-Stuffed Crust Pepperoni Pizza",
                category="Pizza",
                base_price=Decimal("18.98"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['thick crust', 'extra cheese', 'thin crust', 'extra sauce'],
                modification_pricing={
                "thick crust": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "thin crust": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
            },
                keywords=['crust', 'pepperoni-stuffed crust pepperoni', 'pepperoni pizza', 'crust pepperoni pizza', 'pepperoni-stuffed', 'epic', 'pizza', 'crust pepperoni', 'epic pepperoni-stuffed', 'pepperoni', 'epic pepperoni-stuffed crust pepperoni', 'epic pepperoni-stuffed crust', 'pepperoni-stuffed crust', 'pepperoni-stuffed crust pepperoni pizza']
            ),
            MenuItemTemplate(
                name="Epic Stuffed Crust Create Your Own Pizza",
                category="Pizza",
                base_price=Decimal("15.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['thick crust', 'extra cheese', 'thin crust', 'extra sauce'],
                modification_pricing={
                "thick crust": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "thin crust": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
            },
                keywords=['stuffed crust create your own pizza', 'epic', 'pizza', 'stuffed', 'crust create', 'own pizza', 'stuffed crust create your own', 'crust create your', 'epic stuffed crust create your', 'stuffed crust', 'crust create your own', 'crust', 'epic stuffed', 'create', 'create your own', 'own', 'your own', 'epic stuffed crust create', 'create your own pizza', 'stuffed crust create your', 'crust create your own pizza', 'your', 'your own pizza', 'epic stuffed crust create your own', 'stuffed crust create', 'epic stuffed crust', 'create your']
            ),
            MenuItemTemplate(
                name="Parmesan Crusted Create Your Own Papadia",
                category="Main Dish",
                base_price=Decimal("8.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['own papadia', 'parmesan crusted', 'your own papadia', 'crusted create', 'create your own papadia', 'crusted create your own papadia', 'parmesan crusted create your own', 'parmesan', 'crusted', 'create', 'create your own', 'own', 'your own', 'papadia', 'crusted create your own', 'parmesan crusted create your', 'your', 'crusted create your', 'create your', 'parmesan crusted create']
            ),
            MenuItemTemplate(
                name="Sausage",
                category="Main Dish",
                base_price=Decimal("10.98"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=[]
            ),
            MenuItemTemplate(
                name="Extra Cheese",
                category="Main Dish",
                base_price=Decimal("10.98"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['cheese', 'extra']
            ),
            MenuItemTemplate(
                name="Extra Cheesy Alfredo",
                category="Main Dish",
                base_price=Decimal("13.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['cheesy', 'alfredo', 'cheesy alfredo', 'extra cheesy', 'extra']
            ),
            MenuItemTemplate(
                name="Meatball Pepperoni",
                category="Pizza",
                base_price=Decimal("13.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['pepperoni', 'meatball']
            ),
            MenuItemTemplate(
                name="Garden Fresh",
                category="Main Dish",
                base_price=Decimal("13.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['garden', 'fresh']
            ),
            MenuItemTemplate(
                name="Hawaiian BBQ Chicken",
                category="Main Dish",
                base_price=Decimal("13.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['bbq', 'chicken', 'hawaiian bbq', 'hawaiian', 'bbq chicken']
            ),
            MenuItemTemplate(
                name="Crisscut® Fries",
                category="Side Dish",
                base_price=Decimal("3.71"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=['no salt', 'extra crispy', 'extra salt'],
                modification_pricing={
                "no salt": Decimal("0.00"),
                "extra crispy": Decimal("0.50"),
                "extra salt": Decimal("0.50"),
            },
                keywords=['fries', 'crisscut®']
            ),
            MenuItemTemplate(
                name="Hand-Scooped Ice-Cream Shakes™",
                category="Dessert",
                base_price=Decimal("4.82"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['ice-cream', 'hand-scooped ice-cream', 'shakes™', 'hand-scooped', 'ice-cream shakes™']
            ),
            MenuItemTemplate(
                name="Jalapeno Poppers®",
                category="Main Dish",
                base_price=Decimal("4.7"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese'],
                modification_pricing={
                "cheese": Decimal("0.00"),
            },
                keywords=['poppers®', 'jalapeno']
            ),
            MenuItemTemplate(
                name="Double Western Bacon Cheeseburger®",
                category="Burger",
                base_price=Decimal("8.54"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon', 'extra sauce', 'no onions', 'cheese', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "bacon": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['bacon cheeseburger®', 'cheesburger', 'bacon', 'western', 'cheeseburger®', 'double western bacon', 'cheese burger', 'double', 'double western', 'western bacon', 'western bacon cheeseburger®']
            ),
            MenuItemTemplate(
                name="Onion Rings",
                category="Main Dish",
                base_price=Decimal("3.71"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['onion ring', 'onion', 'rings']
            ),
            MenuItemTemplate(
                name="Primal Angus Thickburger",
                category="Burger",
                base_price=Decimal("10.9"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['primal', 'thickburger', 'angus', 'angus thickburger', 'primal angus']
            ),
            MenuItemTemplate(
                name="Single Beyond™ Wraptor Burger",
                category="Burger",
                base_price=Decimal("8.67"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['wraptor burger', 'single beyond™', 'single', 'beyond™', 'wraptor', 'beyond™ wraptor burger', 'single beyond™ wraptor', 'beyond™ wraptor', 'burger']
            ),
            MenuItemTemplate(
                name="Double Beyond™ Wraptor Burger",
                category="Burger",
                base_price=Decimal("14.25"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['double beyond™ wraptor', 'wraptor burger', 'double beyond™', 'double', 'beyond™', 'wraptor', 'beyond™ wraptor burger', 'beyond™ wraptor', 'burger']
            ),
            MenuItemTemplate(
                name="Famous Star® with Cheese",
                category="Salad",
                base_price=Decimal("6.44"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['famous star®', 'star®', 'star® with', 'famous star® with', 'with cheese', 'with', 'star® with cheese', 'cheese', 'famous']
            ),
            MenuItemTemplate(
                name="Beyond Famous Star® with Cheese",
                category="Burger",
                base_price=Decimal("8.67"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['famous star®', 'star®', 'star® with', 'famous star® with', 'beyond famous star®', 'with cheese', 'with', 'star® with cheese', 'cheese', 'famous star® with cheese', 'famous', 'beyond famous', 'beyond', 'beyond famous star® with']
            ),
            MenuItemTemplate(
                name="Super Star® with Cheese",
                category="Salad",
                base_price=Decimal("7.92"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['star®', 'star® with', 'with cheese', 'super', 'super star®', 'with', 'star® with cheese', 'cheese', 'super star® with']
            ),
            MenuItemTemplate(
                name="Western Bacon Cheeseburger®",
                category="Burger",
                base_price=Decimal("7.3"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon', 'extra sauce', 'no onions', 'cheese', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "bacon": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['bacon cheeseburger®', 'cheesburger', 'bacon', 'cheeseburger®', 'western', 'cheese burger', 'western bacon']
            ),
            MenuItemTemplate(
                name="The Big Carl®",
                category="Salad",
                base_price=Decimal("6.93"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['cheese', 'sauce'],
                modification_pricing={
                "cheese": Decimal("0.00"),
                "sauce": Decimal("0.00"),
            },
                keywords=['carl®', 'big', 'the', 'the big', 'big carl®']
            ),
            MenuItemTemplate(
                name="Original Angus Burger",
                category="Burger",
                base_price=Decimal("7.68"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['extra sauce', 'no onions', 'cheese', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['original', 'original angus', 'angus', 'angus burger', 'burger']
            ),
            MenuItemTemplate(
                name="Guacamole Bacon Angus Burger",
                category="Burger",
                base_price=Decimal("8.67"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=['bacon', 'extra sauce', 'no onions', 'cheese', 'extra cheese', 'sauce', 'no pickles'],
                modification_pricing={
                "bacon": Decimal("0.00"),
                "extra sauce": Decimal("0.50"),
                "no onions": Decimal("0.00"),
                "cheese": Decimal("0.00"),
                "extra cheese": Decimal("0.50"),
                "sauce": Decimal("0.00"),
                "no pickles": Decimal("0.00"),
            },
                keywords=['guacamole', 'bacon', 'guacamole bacon angus', 'guacamole bacon', 'angus', 'angus burger', 'bacon angus', 'bacon angus burger', 'burger']
            ),
            MenuItemTemplate(
                name="Large 10 pc Wing Combo",
                category="Side Dish",
                base_price=Decimal("14.09"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['pc wing combo', 'large 10', 'large 10 pc', '10 pc wing combo', 'wing combo', 'large', 'pc', '10 pc', '10', '10 pc wing', 'combo', 'wing', 'pc wing', 'large 10 pc wing']
            ),
            MenuItemTemplate(
                name="10 Wings",
                category="Main Dish",
                base_price=Decimal("10.79"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['wings', '10']
            ),
            MenuItemTemplate(
                name="15 Wings",
                category="Main Dish",
                base_price=Decimal("15.79"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['15', 'wings']
            ),
            MenuItemTemplate(
                name="20 Wings",
                category="Main Dish",
                base_price=Decimal("20.29"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['20', 'wings']
            ),
            MenuItemTemplate(
                name="Large 5 pc Crispy Tender Combo",
                category="Side Dish",
                base_price=Decimal("11.49"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['tender combo', 'pc', 'pc crispy tender', '5 pc', 'large 5 pc', '5 pc crispy tender', 'large', 'large 5 pc crispy tender', 'combo', '5 pc crispy tender combo', 'pc crispy', 'large 5', 'large 5 pc crispy', 'tender', 'crispy tender', 'crispy', '5 pc crispy', '5', 'crispy tender combo', 'pc crispy tender combo']
            ),
            MenuItemTemplate(
                name="Boneless Meal Deal",
                category="Side Dish",
                base_price=Decimal("18.39"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['meal', 'boneless meal', 'meal deal', 'boneless', 'deal']
            ),
            MenuItemTemplate(
                name="Thigh Bites Group Pack",
                category="Side Dish",
                base_price=Decimal("25.99"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['thigh bites group', 'bites group', 'thigh', 'pack', 'thigh bites', 'bites', 'bites group pack', 'group pack', 'group']
            ),
            MenuItemTemplate(
                name="All-In Bundle",
                category="Side Dish",
                base_price=Decimal("26.49"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['all-in', 'bundle']
            ),
            MenuItemTemplate(
                name="Large Thigh Bites",
                category="Main Dish",
                base_price=Decimal("9.69"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['thigh', 'large thigh', 'large', 'thigh bites', 'bites']
            ),
            MenuItemTemplate(
                name="Small 6 pc Wing Combo",
                category="Side Dish",
                base_price=Decimal("11.49"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['pc wing combo', 'small', 'wing combo', 'small 6 pc wing', 'small 6', '6 pc wing', '6 pc', 'small 6 pc', 'pc', '6 pc wing combo', 'combo', 'wing', '6', 'pc wing']
            ),
            MenuItemTemplate(
                name="3 Classic Wings and Regular Thigh Bites Combo",
                category="Side Dish",
                base_price=Decimal("14.99"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['wings and regular thigh bites', 'and regular thigh bites combo', 'thigh bites', 'and regular', 'regular thigh', 'classic', 'wings and regular', 'regular thigh bites combo', 'and', 'classic wings and regular thigh bites combo', 'wings and regular thigh', '3', '3 classic', '3 classic wings and regular thigh', '3 classic wings', 'combo', '3 classic wings and regular', 'and regular thigh', 'classic wings and regular thigh bites', 'wings', 'classic wings and regular', 'thigh bites combo', 'regular thigh bites', 'wings and regular thigh bites combo', 'classic wings and', 'thigh', 'classic wings', '3 classic wings and regular thigh bites', 'regular', '3 classic wings and', 'bites', 'bites combo', 'wings and', 'classic wings and regular thigh', 'and regular thigh bites']
            ),
            MenuItemTemplate(
                name="Medium 8 pc Wing Combo",
                category="Side Dish",
                base_price=Decimal("12.29"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['pc wing combo', 'medium 8', 'wing combo', '8', '8 pc wing combo', 'medium 8 pc', 'medium', '8 pc', 'pc', 'medium 8 pc wing', 'combo', 'wing', '8 pc wing', 'pc wing']
            ),
            MenuItemTemplate(
                name="Regular Thigh Bites Combo",
                category="Side Dish",
                base_price=Decimal("9.79"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['thigh', 'thigh bites combo', 'regular', 'thigh bites', 'regular thigh', 'bites', 'regular thigh bites', 'bites combo', 'combo']
            ),
            MenuItemTemplate(
                name="Large Thigh Bites Combo",
                category="Side Dish",
                base_price=Decimal("13.49"),
                available_sizes=[],
                size_pricing={
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['thigh', 'large thigh', 'large', 'thigh bites combo', 'thigh bites', 'bites', 'bites combo', 'combo', 'large thigh bites']
            ),
            MenuItemTemplate(
                name="Regular Thigh Bites and 3 Classic Wings Combo",
                category="Side Dish",
                base_price=Decimal("14.99"),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                "Small": Decimal("0.00"),
                "Medium": Decimal("0.50"),
                "Large": Decimal("1.00"),
            },
                available_modifications=[],
                modification_pricing={
            },
                keywords=['regular thigh bites and 3', 'thigh bites', 'classic wings combo', 'regular thigh', 'wings combo', 'classic', 'regular thigh bites and 3 classic wings', 'and', 'bites and 3 classic', 'bites and 3', '3', '3 classic', 'regular thigh bites and 3 classic', '3 classic wings combo', 'combo', 'thigh bites and 3', '3 classic wings', 'and 3 classic', 'wings', 'bites and 3 classic wings', 'and 3', 'bites and 3 classic wings combo', 'bites and', 'regular thigh bites', 'and 3 classic wings combo', 'thigh', 'thigh bites and 3 classic wings combo', 'classic wings', 'thigh bites and 3 classic', 'regular', 'regular thigh bites and', 'thigh bites and 3 classic wings', 'bites', 'and 3 classic wings', 'thigh bites and']
            ),
        ]


# Export commonly used types
__all__ = [
    'OrderItem', 'Order', 'Modification', 'MenuItemTemplate', 'OrderSchema',
    'SizeType', 'ModificationType'
]