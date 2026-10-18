
import unittest

from scopeguard import (
    find_explicit_exclusion,
    find_explicit_inclusion,
    quote_is_verified,
)


class TestScopeGuardEvidence(unittest.TestCase):

    def setUp(self):
        self.agreement = (
            "The website will include a responsive design "
            "and a contact form.\n"
            "Payment gateway integration is not included "
            "in this project.\n"
            "The freelancer will deliver the website source code."
        )

    def test_responsive_design_is_included(self):
        quote = find_explicit_inclusion(
            self.agreement,
            "Please make the website responsive.",
        )

        self.assertTrue(quote)
        self.assertIn("responsive design", quote.lower())

    def test_payment_gateway_is_excluded(self):
        quote = find_explicit_exclusion(
            self.agreement,
            "Please add payment gateway integration.",
        )

        self.assertTrue(quote)
        self.assertIn("not included", quote.lower())

    def test_mobile_app_is_not_explicitly_included(self):
        quote = find_explicit_inclusion(
            self.agreement,
            "Please add a mobile app.",
        )

        self.assertEqual(quote, "")

    def test_mobile_app_is_not_explicitly_excluded(self):
        quote = find_explicit_exclusion(
            self.agreement,
            "Please add a mobile app.",
        )

        self.assertEqual(quote, "")

    def test_exact_quote_is_verified(self):
        quote = (
            "Payment gateway integration is not included "
            "in this project."
        )

        self.assertTrue(
            quote_is_verified(quote, self.agreement)
        )

    def test_invented_quote_is_rejected(self):
        quote = "Mobile application development is excluded."

        self.assertFalse(
            quote_is_verified(quote, self.agreement)
        )


    def test_empty_request_has_no_exclusion_match(self):
        quote = find_explicit_exclusion(
            self.agreement,
            ""
        )
        self.assertEqual(quote, "")

    def test_empty_request_has_no_inclusion_match(self):
        quote = find_explicit_inclusion(
            self.agreement,
            ""
        )
        self.assertEqual(quote, "")

    def test_unrelated_quote_is_rejected(self):
        quote = "The project includes a mobile application."
        self.assertFalse(
            quote_is_verified(quote, self.agreement)
        )

    def test_actual_contract_sentence_is_verified(self):
        quote = "The website will include a responsive design and a contact form."
        self.assertTrue(
            quote_is_verified(quote, self.agreement)
        )
        if __name__ == "__main__":
            unittest.main()
