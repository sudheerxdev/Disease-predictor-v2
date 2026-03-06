import pytest
from backend.utils.calculator import bayesian_survival


class TestBayesianSurvivalValidation:
    """Validation tests for the Bayesian survival calculator"""

    # ===== Bounds Tests =====
    def test_valid_result_within_bounds(self):
        """Test that result is always between 0 and 1"""
        assert 0 <= bayesian_survival(0.1, 0.9, 0.05) <= 1
        assert 0 <= bayesian_survival(0.5, 0.5, 0.5) <= 1
        assert 0 <= bayesian_survival(0.01, 0.99, 0.95) <= 1

    @pytest.mark.parametrize("prevalence", [-0.1, 1.1, -1.0, 2.0])
    def test_prevalence_out_of_bounds(self, prevalence):
        """Test that prevalence outside [0, 1] raises ValueError"""
        with pytest.raises(ValueError):
            bayesian_survival(prevalence, 0.9, 0.05)

    @pytest.mark.parametrize("sensitivity", [-0.01, 1.01, -0.5, 1.5])
    def test_sensitivity_out_of_bounds(self, sensitivity):
        """Test that sensitivity outside [0, 1] raises ValueError"""
        with pytest.raises(ValueError):
            bayesian_survival(0.1, sensitivity, 0.05)

    @pytest.mark.parametrize("false_positive", [-0.1, 1.1, -0.5, 1.5])
    def test_false_positive_out_of_bounds(self, false_positive):
        """Test that false positive rate outside [0, 1] raises ValueError"""
        with pytest.raises(ValueError):
            bayesian_survival(0.1, 0.9, false_positive)

    # ===== Type Error Tests =====
    def test_type_errors_with_strings(self):
        """Test that string inputs raise ValueError"""
        with pytest.raises(ValueError):
            bayesian_survival("0.1", 0.9, 0.05)
        with pytest.raises(ValueError):
            bayesian_survival(0.1, "0.9", 0.05)
        with pytest.raises(ValueError):
            bayesian_survival(0.1, 0.9, "0.05")

    def test_type_errors_with_none(self):
        """Test that None inputs raise ValueError"""
        with pytest.raises(ValueError):
            bayesian_survival(None, 0.9, 0.05)
        with pytest.raises(ValueError):
            bayesian_survival(0.1, None, 0.05)
        with pytest.raises(ValueError):
            bayesian_survival(0.1, 0.9, None)

    # ===== Boundary Value Tests =====
    def test_zero_prevalence(self):
        """If disease is not present, posterior should be 0"""
        result = bayesian_survival(0.0, 0.9, 0.05)
        assert result == 0.0

    def test_full_prevalence(self):
        """If disease is always present, posterior should be 1"""
        result = bayesian_survival(1.0, 0.9, 0.05)
        assert result == 1.0

    def test_zero_sensitivity(self):
        """If test never detects the disease, posterior should be 0"""
        result = bayesian_survival(0.5, 0.0, 0.5)
        assert result == 0.0

    def test_full_sensitivity(self):
        """If test always detects the disease, posterior depends on false positive"""
        result = bayesian_survival(0.5, 1.0, 0.5)
        assert 0 <= result <= 1

    # ===== Mid-Range Probability Tests =====
    def test_mid_range_probability_1(self):
        """Test with mid-range values"""
        result = bayesian_survival(0.5, 0.5, 0.5)
        assert result == 0.5

    def test_mid_range_probability_2(self):
        """Test with different mid-range values"""
        result = bayesian_survival(0.3, 0.7, 0.6)
        assert abs(result - 0.5385) < 0.001

    # ===== Low Probability Tests =====
    def test_low_probability_1(self):
        """Test with low probability values"""
        result = bayesian_survival(0.01, 0.01, 0.01)
        assert abs(result - 0.0099) < 0.001

    def test_low_probability_2(self):
        """Test with another set of low values"""
        result = bayesian_survival(0.05, 0.05, 0.05)
        assert abs(result - 0.0526) < 0.001

    # ===== High Probability Tests =====
    def test_high_probability_1(self):
        """Test with high probability values"""
        result = bayesian_survival(0.99, 0.99, 0.99)
        assert abs(result - 0.99) < 0.001

    def test_high_probability_2(self):
        """Test with another set of high values"""
        result = bayesian_survival(0.95, 0.95, 0.95)
        assert abs(result - 0.95) < 0.001

    # ===== Clinical Scenario Tests =====
    def test_clinical_scenario_rare_disease_good_test(self):
        """Rare disease with sensitive and specific test"""
        # Disease prevalence: 1%, Sensitivity: 99%, False Positive: 5%
        result = bayesian_survival(0.01, 0.99, 0.05)
        assert 0.15 < result < 0.20  # Should be around 16.6%

    def test_clinical_scenario_common_disease_moderate_test(self):
        """Common disease with moderate test quality"""
        # Disease prevalence: 10%, Sensitivity: 90%, False Positive: 10%
        result = bayesian_survival(0.10, 0.90, 0.10)
        assert result == 0.5  # Should be around 50%

    def test_clinical_scenario_very_specific_test(self):
        """Very specific test (low false positive rate)"""
        # Disease prevalence: 15%, Sensitivity: 75%, False Positive: 1%
        result = bayesian_survival(0.15, 0.75, 0.01)
        assert 0.91 < result < 0.93  # Should be around 91.9%
