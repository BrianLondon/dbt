from test.integration.base import DBTIntegrationTest

class TestSimpleReference(DBTIntegrationTest):

    def setUp(self):
        DBTIntegrationTest.setUp(self)

        self.run_sql_file("test/integration/003_simple_reference_test/seed.sql")

    @property
    def schema(self):
        return "simple_reference_003"

    @property
    def models(self):
        return "test/integration/003_simple_reference_test/models"

    def test_simple_reference(self):
        self.run_dbt()

        # Copies should match
        self.assertTablesEqual("seed","incremental_copy")
        self.assertTablesEqual("seed","materialized_copy")
        self.assertTablesEqual("seed","view_copy")

        # Summaries should match
        self.assertTablesEqual("summary_expected","incremental_summary")
        self.assertTablesEqual("summary_expected","materialized_summary")
        self.assertTablesEqual("summary_expected","view_summary")
        self.assertTablesEqual("summary_expected","ephemeral_summary")

        self.run_sql_file("test/integration/003_simple_reference_test/update.sql")

        self.run_dbt()

        # Copies should match
        self.assertTablesEqual("seed","incremental_copy")
        self.assertTablesEqual("seed","materialized_copy")
        self.assertTablesEqual("seed","view_copy")

        # Summaries should match
        self.assertTablesEqual("summary_expected","incremental_summary")
        self.assertTablesEqual("summary_expected","materialized_summary")
        self.assertTablesEqual("summary_expected","view_summary")
        self.assertTablesEqual("summary_expected","ephemeral_summary")

    def test_simple_reference_with_models(self):
        # Run materialized_copy, ephemeral_copy, and their dependents
        # ephemeral_copy should not actually be materialized b/c it is ephemeral
        # the dependent ephemeral_summary, however, should be materialized as a table
        self.run_dbt(['run', '--models', 'materialized_copy', 'ephemeral_copy'])

        # Copies should match
        self.assertTablesEqual("seed","materialized_copy")

        # Summaries should match
        self.assertTablesEqual("summary_expected","materialized_summary")
        self.assertTablesEqual("summary_expected","ephemeral_summary")

        created_models = self.get_models_in_schema()

        self.assertFalse('incremental_copy' in created_models)
        self.assertFalse('incremental_summary' in created_models)
        self.assertFalse('view_copy' in created_models)
        self.assertFalse('view_summary' in created_models)

        # make sure this wasn't errantly materialized
        self.assertFalse('ephemeral_copy' in created_models)

        self.assertTrue('materialized_copy' in created_models)
        self.assertTrue('materialized_summary' in created_models)
        self.assertEqual(created_models['materialized_copy'], 'table')
        self.assertEqual(created_models['materialized_summary'], 'table')

        self.assertTrue('ephemeral_summary' in created_models)
        self.assertEqual(created_models['ephemeral_summary'], 'table')
