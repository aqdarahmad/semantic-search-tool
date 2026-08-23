import json
from pathlib import Path

from job_matcher import get_top_jobs
from gemini_evaluator import evaluate_jobs


# ==========================================
# Paths
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

CV_PROFILE_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "candidate_profile.json"
)

RESULTS_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "match_results.json"
)


# ==========================================
# Load Candidate
# ==========================================

def load_candidate():

    with open(
        CV_PROFILE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==========================================
# Calculate Final Score
# ==========================================

def calculate_final_score(
    semantic_score,
    llm_score,
    semantic_weight=0.4,
    llm_weight=0.6
):

    final_score = (
        semantic_score * semantic_weight
        +
        llm_score * llm_weight
    )

    return round(
        final_score,
        2
    )


# ==========================================
# Run Pipeline
# ==========================================

def run_pipeline():

    print("\n======================================")
    print("      CV → JOB MATCHING PIPELINE")
    print("======================================\n")


    # ======================================
    # Step 1
    # ======================================

    print(
        "Step 1: Loading candidate profile..."
    )

    candidate = load_candidate()


    # ======================================
    # Step 2
    # Semantic Search
    # ======================================

    print(
        "Step 2: Finding top jobs using "
        "semantic similarity..."
    )

    top_jobs = get_top_jobs(3)


    print(
        f"\nRetrieved {len(top_jobs)} jobs:"
    )


    for job in top_jobs:

        semantic_score = (
            job["similarity_score"]
            * 100
        )

        print(
            f"  • {job['title']} "
            f"({job['company']}) "
            f"- semantic score: "
            f"{semantic_score:.2f}%"
        )


    # ======================================
    # Step 3
    # Gemini Evaluation
    # ======================================

    print(
        "\nStep 3: Sending Top jobs to Gemini..."
    )

    print(
        "Gemini will evaluate ALL jobs "
        "using ONE request."
    )


    evaluation = evaluate_jobs(
        candidate,
        top_jobs
    )


    evaluations = evaluation[
        "ranked_jobs"
    ]


    # ======================================
    # Step 4
    # Combine Scores
    # ======================================

    print(
        "\nStep 4: Combining semantic "
        "and Gemini scores..."
    )


    # Map Gemini results by job_id
    evaluation_map = {
        item["job_id"]: item
        for item in evaluations
    }


    final_results = []


    for job in top_jobs:

        evaluation = evaluation_map.get(
            job["job_id"]
        )


        if evaluation is None:

            print(
                f"Warning: Gemini did not "
                f"return job {job['job_id']}"
            )

            continue


        semantic_score = (
            job["similarity_score"]
            * 100
        )


        llm_score = (
            evaluation["match_score"]
        )


        final_score = calculate_final_score(
            semantic_score,
            llm_score
        )


        result = {

            "job_id":
                job["job_id"],

            "job_title":
                job["title"],

            "company":
                job["company"],

            "semantic_score":
                round(
                    semantic_score,
                    2
                ),

            "llm_score":
                round(
                    llm_score,
                    2
                ),

            "final_score":
                final_score,

            "decision":
                evaluation["decision"],

            "matching_skills":
                evaluation[
                    "matching_skills"
                ],

            "missing_skills":
                evaluation[
                    "missing_skills"
                ],

            "relevant_experience":
                evaluation[
                    "relevant_experience"
                ],

            "strengths":
                evaluation[
                    "strengths"
                ],

            "weaknesses":
                evaluation[
                    "weaknesses"
                ],

            "reason":
                evaluation[
                    "reason"
                ],

            "recommendation":
                evaluation[
                    "recommendation"
                ]
        }


        final_results.append(
            result
        )


    # ======================================
    # Step 5
    # Final Ranking
    # ======================================

    print(
        "\nStep 5: Ranking jobs..."
    )


    final_results.sort(
        key=lambda x:
            x["final_score"],
        reverse=True
    )


    # ======================================
    # Step 6
    # Save Results
    # ======================================

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            final_results,
            file,
            indent=4,
            ensure_ascii=False
        )


    # ======================================
    # Final Output
    # ======================================

    print(
        "\n======================================"
    )

    print(
        "             FINAL RANKING"
    )

    print(
        "======================================\n"
    )


    for rank, result in enumerate(
        final_results,
        start=1
    ):

        print(
            f"{rank}. "
            f"{result['job_title']}"
        )

        print(
            f"   Company: "
            f"{result['company']}"
        )

        print(
            f"   Semantic Score: "
            f"{result['semantic_score']:.2f}%"
        )

        print(
            f"   Gemini Score: "
            f"{result['llm_score']:.2f}%"
        )

        print(
            f"   FINAL SCORE: "
            f"{result['final_score']:.2f}%"
        )

        print(
            f"   Decision: "
            f"{result['decision']}"
        )

        print(
            "--------------------------------------"
        )


    print(
        "\nResults saved to:"
    )

    print(
        RESULTS_PATH
    )


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    run_pipeline()