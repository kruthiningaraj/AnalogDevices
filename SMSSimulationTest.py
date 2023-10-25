import queue
import string
import unittest
from io import StringIO
from unittest.mock import patch
from SMSSimulation import SMSSimulation


class TestSMSSimulation(unittest.TestCase):
    """
    Test class for SMSSimulation.
    """
    def test_generate_random_message_length(self):
        """
        Test that the generate_random_message function returns a string of length between 1 and 100
        """
        self.simulation = SMSSimulation(
            message_count=100,
            message_queue=None,
            senders_count=5,
            sender_processing_times=None,
            sender_failure_rates=None,
            progress_monitor_update_interval=5,
        )

        message = self.simulation.generate_random_message()

        self.assertGreaterEqual(len(message), 1)
        self.assertLessEqual(len(message), 100)

    def test_generate_random_message_characters(self):
        """
        Test that the generate_random_message function returns a string with only valid characters.
        """
        self.simulation = SMSSimulation(
            message_count=100,
            message_queue=None,
            senders_count=5,
            sender_processing_times=None,
            sender_failure_rates=None,
            progress_monitor_update_interval=5,
        )

        message = self.simulation.generate_random_message()

        valid_characters = string.ascii_letters + string.digits + string.punctuation + string.whitespace
        self.assertTrue(all(char in valid_characters for char in message))

    def test_producer(self):
        """
        Test that the producer function puts the correct number of messages in the message queue.
        """
        self.simulation = SMSSimulation(
            message_count=100,
            message_queue=queue.Queue(),
            senders_count=5,
            sender_processing_times=None,
            sender_failure_rates=None,
            progress_monitor_update_interval=5,
        )

        self.simulation.producer()

        self.assertEqual(self.simulation.message_queue.qsize(), 100)

    def test_sender_successful_message(self):
        """
        Test that the sender function increments the success_messages variable when a message is successfully sent.
        """
        self.simulation = SMSSimulation(
            message_count=100,
            message_queue=queue.Queue(),
            senders_count=5,
            sender_processing_times=[0.2, 0.3, 0.4, 0.5, 0.6],
            sender_failure_rates=[0.05, 0.1, 0.15, 0.2, 0.25],
            progress_monitor_update_interval=5,
        )

        self.simulation.message_queue.put("Testing message")
        self.simulation.sender(processing_mean_time=1.0, failure_rate=0.0)

        self.assertEqual(self.simulation.success_messages, 1)

    def test_sender_failed_message(self):
        """
        Test that the sender function increments the failed_messages variable when a message fails to send.
        """
        self.simulation = SMSSimulation(
            message_count=100,
            message_queue=queue.Queue(),
            senders_count=5,
            sender_processing_times=[0.2, 0.3, 0.4, 0.5, 0.6],
            sender_failure_rates=[0.05, 0.1, 0.15, 0.2, 0.25],
            progress_monitor_update_interval=5,
        )

        self.simulation.message_queue.put("Testing message")
        self.simulation.sender(processing_mean_time=1.0, failure_rate=1.0)

        self.assertEqual(self.simulation.failed_messages, 1)

    def test_progress_monitor(self):
        """
        Test that the progress_monitor function prints the correct output.
        """
        self.simulation = SMSSimulation(
            message_count=100,
            message_queue=queue.Queue(),
            senders_count=5,
            sender_processing_times=[0.2, 0.3, 0.4, 0.5, 0.6],
            sender_failure_rates=[0.05, 0.1, 0.15, 0.2, 0.25],
            progress_monitor_update_interval=0,
        )
        self.simulation.set_simulation_variable_for_testing(success_messages=10, failed_messages=5,
                                                            total_processing_time=20.0)

        # Mocking the self.message_queue.empty() method to return False and then True
        with patch.object(self.simulation.message_queue, 'empty', side_effect=[False, True]):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                # Call to progress_monitor function
                self.simulation.progress_monitor()
            # Capturing the output of the progress_monitor function
            actual_output = mock_stdout.getvalue()

        expected_output = "Messages sent: 10, Messages failed: 5, Avg Time per message: 1.33 seconds\n"
        self.assertEqual(actual_output, expected_output)


if __name__ == '__main__':
    unittest.main()
