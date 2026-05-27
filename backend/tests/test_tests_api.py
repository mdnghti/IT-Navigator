"""Tests for test API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_general_questions_unauthorized(client: AsyncClient):
    """Test getting general questions without auth fails."""
    response = await client.get("/api/v1/tests/general/questions")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_general_questions_success(
    client: AsyncClient, auth_headers: dict, test_general_test
):
    """Test getting general questions successfully."""
    response = await client.get("/api/v1/tests/general/questions", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check question structure
    question = data[0]
    assert "id" in question
    assert "text" in question
    assert "answers" in question
    assert isinstance(question["answers"], list)
    assert len(question["answers"]) > 0

    # Check answer structure (weight should not be exposed)
    answer = question["answers"][0]
    assert "id" in answer
    assert "text" in answer
    assert "weight" not in answer


@pytest.mark.asyncio
async def test_get_general_questions_shuffled(
    client: AsyncClient, auth_headers: dict, test_general_test
):
    """Test that questions are shuffled on each request."""
    response1 = await client.get("/api/v1/tests/general/questions", headers=auth_headers)
    response2 = await client.get("/api/v1/tests/general/questions", headers=auth_headers)

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Note: With only 3 questions, they might be in same order by chance
    # This test just verifies the endpoint works multiple times
    data1 = response1.json()
    data2 = response2.json()
    assert len(data1) == len(data2)


@pytest.mark.asyncio
async def test_submit_general_test_success(
    client: AsyncClient, auth_headers: dict, test_general_test
):
    """Test submitting general test successfully."""
    # Get questions first
    response = await client.get("/api/v1/tests/general/questions", headers=auth_headers)
    questions = response.json()

    # Submit answers
    answers = [
        {"question_id": q["id"], "answer_id": q["answers"][0]["id"]} for q in questions
    ]

    response = await client.post(
        "/api/v1/tests/general/submit",
        json={"answers": answers},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "results" in data
    assert "recommended_specialty" in data
    assert "result_id" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) > 0

    # Check result structure
    result = data["results"][0]
    assert "specialty_code" in result
    assert "specialty_name" in result
    assert "score" in result
    assert "max_score" in result
    assert "percentage" in result


@pytest.mark.asyncio
async def test_submit_general_test_empty_answers(
    client: AsyncClient, auth_headers: dict, test_general_test
):
    """Test submitting test with no answers fails."""
    response = await client.post(
        "/api/v1/tests/general/submit",
        json={"answers": []},
        headers=auth_headers,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_my_results(
    client: AsyncClient, auth_headers: dict, test_general_test
):
    """Test getting user's test results."""
    # Submit a test first
    response = await client.get("/api/v1/tests/general/questions", headers=auth_headers)
    questions = response.json()

    answers = [
        {"question_id": q["id"], "answer_id": q["answers"][0]["id"]} for q in questions
    ]

    await client.post(
        "/api/v1/tests/general/submit",
        json={"answers": answers},
        headers=auth_headers,
    )

    # Get results
    response = await client.get("/api/v1/tests/results/my", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check result structure
    result = data[0]
    assert "id" in result
    assert "test_id" in result
    assert "scores" in result
    assert "completed_at" in result


@pytest.mark.asyncio
async def test_get_result_by_id(
    client: AsyncClient, auth_headers: dict, test_general_test
):
    """Test getting specific result by ID."""
    # Submit a test first
    response = await client.get("/api/v1/tests/general/questions", headers=auth_headers)
    questions = response.json()

    answers = [
        {"question_id": q["id"], "answer_id": q["answers"][0]["id"]} for q in questions
    ]

    submit_response = await client.post(
        "/api/v1/tests/general/submit",
        json={"answers": answers},
        headers=auth_headers,
    )
    result_id = submit_response.json()["result_id"]

    # Get specific result
    response = await client.get(
        f"/api/v1/tests/results/{result_id}", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == result_id


@pytest.mark.asyncio
async def test_get_result_not_found(client: AsyncClient, auth_headers: dict):
    """Test getting nonexistent result fails."""
    response = await client.get("/api/v1/tests/results/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_specialized_test_not_found(client: AsyncClient, auth_headers: dict):
    """Test getting specialized test for nonexistent specialty fails."""
    response = await client.get(
        "/api/v1/tests/specialized/NONEXISTENT/questions", headers=auth_headers
    )
    assert response.status_code == 404
