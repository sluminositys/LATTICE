from lattice.verification import ClaimVerifier


def test_claim_verifier_is_not_applicable_without_claims() -> None:
    report = ClaimVerifier().verify([])

    assert report.final_claim_status == "not_applicable"


def test_claim_verifier_marks_claims_unsupported_until_evidence_exists() -> None:
    report = ClaimVerifier().verify(["Claim A is supported"])

    assert report.final_claim_status == "unsupported"
    assert report.unsupported_claims == ["Claim A is supported"]
