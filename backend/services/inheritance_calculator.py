"""
حاسبة توزيع الإعانات حسب قواعد الميراث الشرعي
"""
from typing import List, Dict, Any
from fractions import Fraction


# قاموس تحويل النسب الرقمية إلى ألفاظ عربية شرعية
ARABIC_FRACTIONS = {
    Fraction(1, 2): "نصف",
    Fraction(1, 4): "ربع",
    Fraction(1, 8): "ثمن",
    Fraction(1, 3): "ثلث",
    Fraction(2, 3): "ثلثان",
    Fraction(1, 6): "سدس",
}


def fraction_to_arabic(frac: Fraction) -> str:
    """تحويل الكسر إلى اسم عربي شرعي"""
    if frac in ARABIC_FRACTIONS:
        return ARABIC_FRACTIONS[frac]
    return f"{frac.numerator}/{frac.denominator}"


class InheritanceCalculator:
    """حاسبة توزيع الإعانات على المستحقين"""
    
    RELATION_TYPES = {
        "زوج": "husband",
        "زوجة": "wife",
        "أب": "father",
        "أم": "mother",
        "ابن": "son",
        "ابنة": "daughter",
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
            elif relation == "ابنة":
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
        """تحويل الحصص إلى مبالغ فعلية مع التفسير"""
        results = []
        
        # تحديد وجود الأبناء
        has_children = any(s["relation"] in ["ابن", "ابنة"] for s in shares)
        
        for share_data in shares:
            share_fraction = share_data["share"]
            amount = float(share_fraction) * self.total_amount
            relation = share_data["relation"]
            
            # تحديد نوع الاستحقاق والتفسير
            inheritance_type, explanation = self._generate_explanation(
                relation, share_fraction, share_data["name"], has_children
            )
            
            # تحويل النسبة إلى اسم عربي
            arabic_fraction = fraction_to_arabic(share_fraction)
            
            results.append({
                "name": share_data["name"],
                "relation": share_data["relation"],
                "percentage": f"{share_fraction.numerator}/{share_fraction.denominator}",
                "percentage_arabic": arabic_fraction,
                "share_decimal": float(share_fraction),
                "amount": round(amount, 2),
                "inheritance_type": inheritance_type,
                "explanation": explanation,
            })
        
        return results
    
    def _generate_explanation(self, relation: str, share: Fraction, name: str, has_children: bool) -> tuple:
        """توليد التفسير الشرعي لكل مستحق"""
        arabic_share = fraction_to_arabic(share)
        
        if relation == "زوج":
            if has_children:
                return ("فرض", f"زوجته {name} وتستحق {arabic_share} تركته فرضًا لوجود الفرع الوارث")
            else:
                return ("فرض", f"زوجته {name} وتستحق {arabic_share} تركته فرضًا لعدم وجود الفرع الوارث")
        
        elif relation == "زوجة":
            if has_children:
                return ("فرض", f"زوجته {name} وتستحق {arabic_share} تركته فرضًا لوجود الفرع الوارث")
            else:
                return ("فرض", f"زوجته {name} وتستحق {arabic_share} تركته فرضًا لعدم وجود الفرع الوارث")
        
        elif relation == "أم":
            if has_children:
                return ("فرض", f"والدته {name} وتستحق {arabic_share} تركته فرضًا لوجود الفرع الوارث")
            else:
                return ("فرض", f"والدته {name} وتستحق {arabic_share} تركته فرضًا لعدم وجود الفرع الوارث")
        
        elif relation == "أب":
            if has_children:
                return ("فرض", f"والده {name} ويستحق {arabic_share} تركته فرضًا لوجود الفرع الوارث")
            else:
                # الأب يأخذ الباقي تعصيبًا
                return ("تعصيب", f"والده {name} ويستحق الباقي تعصيبًا لعدم وجود الفرع الوارث")
        
        elif relation == "ابن":
            return ("تعصيب", f"ابنه {name} ويستحق نصيبه من الباقي تعصيبًا للذكر مثل حظ الأنثيين")
        
        elif relation == "ابنة":
            # التحقق من عدد البنات
            daughters_count = sum(1 for s in self.beneficiaries if s.get("relation") == "ابنة")
            if daughters_count == 1 and not any(s.get("relation") == "ابن" for s in self.beneficiaries):
                # بنت واحدة بدون إخوة ذكور
                if share == Fraction(1, 2):
                    return ("فرض", f"ابنته {name} وتستحق {arabic_share} تركته فرضًا لانفرادها")
                else:
                    return ("رد", f"ابنته {name} وتستحق نصيبها فرضًا والباقي ردًا")
            elif daughters_count >= 2 and not any(s.get("relation") == "ابن" for s in self.beneficiaries):
                # بنتان أو أكثر بدون إخوة ذكور
                if arabic_share == "ثلثان":
                    return ("فرض", f"ابنته {name} وتستحق نصيبها من {arabic_share} التركة فرضًا")
                else:
                    return ("فرض + رد", f"ابنته {name} وتستحق نصيبها من الفرض والباقي ردًا")
            else:
                # بنات مع أبناء
                return ("تعصيب", f"ابنته {name} وتستحق نصيبها من الباقي تعصيبًا للذكر مثل حظ الأنثيين")
        
        return ("", f"{name}")
    
    def generate_summary_explanation(self) -> str:
        """توليد ملخص نصي كامل للحالة"""
        if not self.results:
            return ""
        
        lines = []
        
        # تجميع حسب نوع الاستحقاق
        froud = [r for r in self.results if r.get("inheritance_type") == "فرض"]
        tasseeb = [r for r in self.results if r.get("inheritance_type") == "تعصيب"]
        rad = [r for r in self.results if "رد" in r.get("inheritance_type", "")]
        
        # الفروض
        if froud:
            lines.append("**الفروض:**")
            for ben in froud:
                lines.append(f"• {ben['explanation']}")
        
        # التعصيب
        if tasseeb:
            lines.append("\n**التعصيب:**")
            sons = [r for r in tasseeb if r["relation"] == "ابن"]
            daughters = [r for r in tasseeb if r["relation"] == "ابنة"]
            fathers = [r for r in tasseeb if r["relation"] == "أب"]
            
            if sons or daughters:
                names = []
                if sons:
                    names.extend([s["name"] for s in sons])
                if daughters:
                    names.extend([d["name"] for d in daughters])
                
                names_str = " و".join(names)
                lines.append(f"• أولاده {names_str} يستحقون الباقي تعصيبًا للذكر مثل حظ الأنثيين")
            
            if fathers:
                for f in fathers:
                    lines.append(f"• {f['explanation']}")
        
        # الرد
        if rad:
            lines.append("\n**الرد:**")
            lines.append("• الباقي بعد الفروض يُرد على أصحاب الفروض بحسب أنصبتهم الشرعية")
        
        return "\n".join(lines)
    
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
        dict: النتائج مع التحقق والتفسير
    """
    calculator = InheritanceCalculator(total_amount, beneficiaries)
    results = calculator.calculate()
    validation = calculator.validate()
    summary = calculator.generate_summary_explanation()
    
    return {
        "results": results,
        "validation": validation,
        "summary_explanation": summary,
    }
