from mizu_validator.classifier import classify
from mizu_validator.embeddings.domain_embeddings import V1_EMBEDDING

def test_classify():
    # Given
    text = "Coding"

    # When
    res = classify(text, V1_EMBEDDING, 2)

    # Then
    assert res == ["Coding", "Codes"]
