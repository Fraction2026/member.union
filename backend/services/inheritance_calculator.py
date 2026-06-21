"""
حاسبة توزيع الإعانات حسب قواعد الميراث الشرعي
"""
from typing import List, Dict, Any
from fractions import Fraction


class InheritanceCalculator:
    """حاسبة توزيع الإعانات على المستحقين"""
    
    RELATION_TYPES = {
        "زوج": "husband",
        "زوجة": "wife",
        "أب": "father",
        "أم": "mother",
        "ابن": "son",
        "بنت": "daughter",
    }
    
    def __init__(self, total_amount: float, beneficiaries: List[Dict[str, Any]]):
        """
        Args:
            total_amount: أصل المبلغ المعتمد
            beneficiaries: قائمة المستحقين [{"name": "...", "relation": "زوج/زوجة/..."}]
        """
        self.total_amount = total_amount
        self.beneficiaries = beneficiaries
        self.results = []
        
    def calculate(self) -> List[Dict[str, Any]]:
        """حساب التوزيع وإرجاع النتائج"""
        if not self.beneficiaries:
            return []
        
        # تصنيف المستحقين
        classified = self._classify_beneficiaries()
        
        # حساب الحصص
        shares = self._calculate_shares(classified)
        
        # تحويل الحصص إلى مبالغ
        self.results = self._convert_to_amounts(shares)
        
        return self.results
    
    def _classify_beneficiaries(self) -> Dict[str, Any]:
        """تصنيف المستحقين حسب درجة القرابة"""
        classified = {
            "husbands": [],
            "wives": [],
            "father": None,
            "mother": None,
            "sons": [],
            "daughters": [],
        }
        
        for b in self.beneficiaries:
            relation = b.get("relation", "")
            if relation == "زوج":
                classified["husbands"].append(b)
            elif relation == "زوجة":
                classified["wives"].append(b)
            elif relation == "أب":
                classified["father"] = b
            elif relation == "أم":
                classified["mother"] = b
            elif relation == "ابن":
                classified["sons"].append(b)
            elif relation == "بنت":
                classified["daughters"].append(b)
        
        return classified
    
    def _calculate_shares(self, classified: Dict[str, Any]) -> List[Dict[str, Any]]:
        """حساب الحصص حسب قواعد الميراث"""
        shares = []
        
        # تحديد وجود الأبناء (ذكور أو إناث)
        has_children = len(classified["sons"]) > 0 or len(classified["daughters"]) > 0
        
        # المتبقي بعد الفروض
        remaining = Fraction(1)
        
        # 1. الزوج/الزوجة
        if classified["husbands"]:
            # الزوج: 1/2 بدون أبناء، 1/4 مع أبناء
            husband_share = Fraction(1, 4) if has_children else Fraction(1, 2)
            for husband in classified["husbands"]:
                shares.append({
                    "name": husband["name"],
                    "relation": "زوج",
                    "share": husband_share,
                })
                remaining -= husband_share
        
        if classified["wives"]:
            # الزوجة: 1/4 بدون أبناء، 1/8 مع أبناء
            wife_share_total = Fraction(1, 8) if has_children else Fraction(1, 4)
            # إذا كان هناك أكثر من زوجة، يُقسم نصيبهن بينهن بالتساوي
            wife_share_each = wife_share_total / len(classified["wives"])
            for wife in classified["wives"]:
                shares.append({
                    "name": wife["name"],
                    "relation": "زوجة",
                    "share": wife_share_each,
                })
            remaining -= wife_share_total
        
        # 2. الأم
        if classified["mother"]:
            # الأم: 1/3 بدون أبناء، 1/6 مع أبناء
            mother_share = Fraction(1, 6) if has_children else Fraction(1, 3)
            shares.append({
                "name": classified["mother"]["name"],
                "relation": "أم",
                "share": mother_share,
            })
            remaining -= mother_share
        
        # 3. الأب
        if classified["father"]:
            if has_children:
                # الأب: 1/6 مع الأبناء
                father_share = Fraction(1, 6)
                shares.append({
                    "name": classified["father"]["name"],
                    "relation": "أب",
                    "share": father_share,
                })
                remaining -= father_share
            else:
                # إذا لم يكن هناك أبناء، الأب يأخذ الباقي (سيُحسب لاحقاً)
                pass
        
        # 4. الأبناء والبنات
        if has_children:
            # توزيع الباقي: للذكر مثل حظ الأنثيين
            sons_count = len(classified["sons"])
            daughters_count = len(classified["daughters"])
            
            # حساب عدد الأسهم: كل ابن = سهمان، كل بنت = سهم واحد
            total_parts = (sons_count * 2) + daughters_count
            
            if total_parts > 0:
                # حصة كل سهم
                one_part = remaining / total_parts
                
                # توزيع على الأبناء
                for son in classified["sons"]:
                    shares.append({
                        "name": son["name"],
                        "relation": "ابن",
                        "share": one_part * 2,  # سهمان
                    })
                
                # توزيع على البنات
                for daughter in classified["daughters"]:
                    shares.append({
                        "name": daughter["name"],
                        "relation": "بنت",
                        "share": one_part,  # سهم واحد
                    })
                
                remaining = Fraction(0)
        else:
            # إذا لم يكن هناك أبناء والأب موجود، يأخذ الباقي
            if classified["father"]:
                shares.append({
                    "name": classified["father"]["name"],
                    "relation": "أب",
                    "share": remaining,
                })
                remaining = Fraction(0)
        
        return shares
    
    def _convert_to_amounts(self, shares: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """تحويل الحصص إلى مبالغ فعلية"""
        results = []
        
        for share_data in shares:
            share_fraction = share_data["share"]
            amount = float(share_fraction) * self.total_amount
            
            results.append({
                "name": share_data["name"],
                "relation": share_data["relation"],
                "percentage": f"{share_fraction.numerator}/{share_fraction.denominator}",
                "share_decimal": float(share_fraction),
                "amount": round(amount, 2),
            })
        
        return results
    
    def get_total_distributed(self) -> float:
        """الحصول على إجمالي المبالغ الموزعة"""
        return sum(r["amount"] for r in self.results)
    
    def validate(self) -> Dict[str, Any]:
        """التحقق من صحة التوزيع"""
        total_distributed = self.get_total_distributed()
        difference = abs(self.total_amount - total_distributed)
        
        return {
            "is_valid": difference < 0.01,  # فرق أقل من قرش واحد
            "total_amount": self.total_amount,
            "total_distributed": total_distributed,
            "difference": difference,
        }


def calculate_inheritance(total_amount: float, beneficiaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    دالة مساعدة لحساب التوزيع
    
    Args:
        total_amount: أصل المبلغ
        beneficiaries: قائمة المستحقين
    
    Returns:
        dict: النتائج مع التحقق
    """
    calculator = InheritanceCalculator(total_amount, beneficiaries)
    results = calculator.calculate()
    validation = calculator.validate()
    
    return {
        "results": results,
        "validation": validation,
    }
