import io
import unittest
import zipfile

from app import app


class AppTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Agentic Presentation Builder", response.data)

    def test_generate_school_project(self):
        response = self.client.post(
            "/generate",
            data={
                "presentation_type": "school_project",
                "title": "Example Project",
                "presenters": "Student One",
                "problem": "A real problem statement.",
                "output_target": "overleaf",
                "compiler": "pdflatex",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Package generated", response.data)
        self.assertIn(b"organisation:\n  enabled: false", response.data)


    def test_generate_internship_with_organisation(self):
        response = self.client.post(
            "/generate",
            data={
                "presentation_type": "internship",
                "title": "Internship Project",
                "presenters": "Student One",
                "problem": "A real internship problem.",
                "organisation_name": "Example Company",
                "organisation_department": "Engineering",
                "output_target": "overleaf",
                "compiler": "pdflatex",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"organisation:\n  enabled: true", response.data)
        self.assertIn(b"name: Example Company", response.data)

    def test_internship_missing_organisation_preserves_form(self):
        response = self.client.post(
            "/generate",
            data={
                "presentation_type": "internship",
                "title": "Internship Project",
                "presenters": "Student One",
                "problem": "A real internship problem.",
                "output_target": "overleaf",
                "compiler": "pdflatex",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Organisation name is required", response.data)
        self.assertIn(b'"presentation_type": "internship"', response.data)
        self.assertIn(b'data-initial-step="2"', response.data)

    def test_american_organization_alias_is_accepted(self):
        response = self.client.post(
            "/generate",
            data={
                "presentation_type": "internship",
                "title": "Internship Project",
                "presenters": "Student One",
                "problem": "A real internship problem.",
                "organization_name": "Alias Company",
                "output_target": "overleaf",
                "compiler": "pdflatex",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"name: Alias Company", response.data)

    def test_package_generated_tex(self):
        tex = r"\documentclass{beamer}\begin{document}\begin{frame}OK\end{frame}\end{document}"
        response = self.client.post(
            "/package-generated",
            data={"package_target": "local", "main_tex": tex},
        )
        self.assertEqual(response.status_code, 200)
        with zipfile.ZipFile(io.BytesIO(response.data)) as archive:
            self.assertIn("main.tex", archive.namelist())
            self.assertIn("compile.sh", archive.namelist())
            self.assertIn("compile.ps1", archive.namelist())


if __name__ == "__main__":
    unittest.main()
