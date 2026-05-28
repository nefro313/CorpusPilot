from core.config import Settings


def test_cors_origins_list_splits_and_trims() -> None:
    settings = Settings(cors_origins="http://a.com, http://b.com ,  ")
    assert settings.cors_origins_list == ["http://a.com", "http://b.com"]


def test_milvus_search_params_uses_metric_type() -> None:
    settings = Settings(milvus_metric_type="L2")
    assert settings.milvus_search_params == {"metric_type": "L2"}


def test_default_chat_model_constants_are_sane() -> None:
    settings = Settings()
    assert settings.embedding_dimensions > 0
    assert 0 < settings.eval_min_faithfulness <= 1
    assert 0 < settings.eval_min_factual_correctness <= 1
    assert 0 < settings.eval_min_context_recall <= 1
