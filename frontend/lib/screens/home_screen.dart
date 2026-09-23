import 'package:flutter/material.dart';
import 'learner_profile_screen.dart';
import 'tutor_profile_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Peer Tutoring Platform")),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                "AI-Based Peer Tutoring\nMatching Platform",
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                "Review-2 prototype",
                style: TextStyle(color: Colors.grey),
              ),
              const SizedBox(height: 40),
              ElevatedButton(
                style: ElevatedButton.styleFrom(minimumSize: const Size(240, 48)),
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const LearnerProfileScreen()),
                ),
                child: const Text("I'm a Learner"),
              ),
              const SizedBox(height: 16),
              OutlinedButton(
                style: OutlinedButton.styleFrom(minimumSize: const Size(240, 48)),
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const TutorProfileScreen()),
                ),
                child: const Text("I'm a Tutor"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
