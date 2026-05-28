from domain.profiles import (
    DOMAIN_PROFILES,
    CorpusDomain,
    get_domain_profile,
    list_domain_profiles,
)


def test_every_corpus_domain_has_a_profile() -> None:
    for domain in CorpusDomain:
        profile = get_domain_profile(domain)
        assert profile.value == domain
        assert profile.label
        assert profile.description
        assert profile.chunk_size > 0
        assert 0 <= profile.chunk_overlap < profile.chunk_size
        assert profile.retrieval_k >= profile.rerank_k > 0


def test_list_domain_profiles_matches_enum_order() -> None:
    enum_order = list(CorpusDomain)
    listed = list_domain_profiles()
    assert [p.value for p in listed] == enum_order


def test_domain_profiles_registry_has_no_extras() -> None:
    assert set(DOMAIN_PROFILES.keys()) == set(CorpusDomain)
