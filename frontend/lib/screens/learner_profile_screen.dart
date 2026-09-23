import 'package:flutter/material.dart';
import '../models/learner.dart';
import '../services/api_service.dart';
import 'recommendation_screen.dart';

const List<String> kPreferences = ["Visual", "Auditory", "Reading/Writing", "Kinesthetic"];
const List<String> kAvailabilitySlots = ["Morning", "Afternoon", "Evening", "Weekend"];

class LearnerProfileScreen extends StatefulWidget {
  const LearnerProfileScreen({super.key});

  @override
  State<LearnerProfileScreen> createState() => _LearnerProfileScreenState();
}

class _LearnerProfileScreenState extends State<LearnerProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _subjectsController = TextEditingController();

  String? _preference;
  final Set<String> _availability = {};
  bool _submitting = false;

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_preference == null) {
      _showError("Please select a learning preference.");
      return;
    }
    if (_availability.isEmpty) {
      _showError("Please select at least one availability slot.");
      return;
    }

    setState(() => _submitting = true);
    try {
      final learner = Learner(
        name: _nameController.text.trim(),
        email: _emailController.text.trim(),
        subjects: _subjectsController.text.split(",").map((s) => s.trim()).where((s) => s.isNotEmpty).toList(),
        learningPreference: _preference!,
        availability: _availability.toList(),
      );
      final created = await ApiService.createLearner(learner);

      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => RecommendationScreen(learnerId: created.id!)),
      );
    } catch (e) {
      _showError("Could not save profile: $e");
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Learner Profile")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: "Name"),
                validator: (v) => (v == null || v.trim().isEmpty) ? "Name is required" : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: "Email"),
                keyboardType: TextInputType.emailAddress,
                validator: (v) => (v == null || !v.contains("@")) ? "Enter a valid email" : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _subjectsController,
                decoration: const InputDecoration(
                  labelText: "Subjects/topics required",
                  hintText: "e.g. Java, DSA",
                ),
                validator: (v) => (v == null || v.trim().isEmpty) ? "Enter at least one subject" : null,
              ),
              const SizedBox(height: 20),
              const Text("Learning preference", style: TextStyle(fontWeight: FontWeight.bold)),
              Wrap(
                spacing: 8,
                children: kPreferences
                    .map((p) => ChoiceChip(
                          label: Text(p),
                          selected: _preference == p,
                          onSelected: (_) => setState(() => _preference = p),
                        ))
                    .toList(),
              ),
              const SizedBox(height: 20),
              const Text("Availability", style: TextStyle(fontWeight: FontWeight.bold)),
              Wrap(
                spacing: 8,
                children: kAvailabilitySlots
                    .map((slot) => FilterChip(
                          label: Text(slot),
                          selected: _availability.contains(slot),
                          onSelected: (selected) => setState(() {
                            selected ? _availability.add(slot) : _availability.remove(slot);
                          }),
                        ))
                    .toList(),
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: _submitting ? null : _submit,
                child: _submitting
                    ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Text("Save & Find Tutors"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
