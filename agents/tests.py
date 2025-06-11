from django.test import TestCase

from agents.models import AgentModel


# Create your tests here.
class AgentModelTestCase(TestCase):
    def setUp(self):
        # Set up any necessary data for the tests
        self.agent = AgentModel.objects.create(
            name="Test Agent", instructions="Test instructions"
        )

    def test_agent_creation(self):
        # Test that the agent was created successfully
        self.assertEqual(self.agent.name, "Test Agent")
        self.assertEqual(self.agent.instructions, "Test instructions")

    def test_agent_str(self):
        # Test the string representation of the agent
        self.assertEqual(str(self.agent), "Test Agent")
