import requests

base_url = "http://localhost:8001"

def test_pu_and_degree():
    # Authenticate as Central Platform Admin to query structure for other institutions
    login_res = requests.post(f"{base_url}/auth/login", data={
        "username": "admin.central@nagriksetu.gov",
        "password": "Central@NagrikSetu2026!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- TEST: PU College Structure (SCH011) ---")
    pu_res = requests.get(f"{base_url}/institution/SCH011/academic-structure", headers=headers)
    assert pu_res.status_code == 200
    pu_data = pu_res.json()
    print("PU Category:", pu_data.get("category"))
    print("PU Levels:", pu_data.get("pu_levels"))
    print("PU Streams:", pu_data.get("streams"))
    print("PU Combinations:", pu_data.get("combinations"))
    assert "Science" in pu_data.get("streams", [])
    assert "Commerce" in pu_data.get("streams", [])

    print("\n--- TEST: Degree College Structure (COL001) ---")
    deg_res = requests.get(f"{base_url}/institution/COL001/academic-structure", headers=headers)
    assert deg_res.status_code == 200
    deg_data = deg_res.json()
    print("Degree Category:", deg_data.get("category_type"))
    print("Programs count:", len(deg_data.get("programs", [])))
    print("Years of study:", deg_data.get("years_of_study"))
    print("Semesters:", deg_data.get("semesters"))
    assert deg_data.get("category_type") == "DEGREE_COLLEGE"

    print("\nPU College and Degree College structures verified successfully!")

if __name__ == "__main__":
    test_pu_and_degree()
