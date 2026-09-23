import 'package:flutter/material.dart';
import '../models/tutor.dart';
import '../services/api_service.dart';
import 'learner_profile_screen.dart' show kPreferences, kAvailabilitySlots;

class TutorProfileScreen extends StatefulWidget {
  const TutorProfileScreen({super.key});

  @override
  State<TutorProfileScreen> createState() => _TutorProfileScreenState();
}

class _TutorProfileScreenState extends State<TutorProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _subjectsController = TextEditingController();

  String? _preference;
  int _expertiseLevel = 3;
  final Set<String> _availability = {};
  bool _submitting = false;

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_preference == null) {
      _showError("Please select a teaching preference.");
      return;
    }
    if (_availability.isEmpty) {
      _showError("Please select at least one availability slot.");
      return;
    }

    setState(() => _submitting = true);
    try {
      final tutor = Tutor(
        name: _nameController.text.trim(),
        email: _emailController.text.trim(),
        subjects: _subjectsController.text.split(",").map((s) => s.trim()).where((s) => s.isNotEmpty).toList(),
        expertiseLevel: _expertiseLevel,
        teachingPreference: _preference!,
        availability: _availability.toList(),
      );
      await ApiService.createTutor(tutor);

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Tutor profile saved successfully.")),
      );
      Navigator.pop(context);
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
      appBar: AppBar(title: const Text("Tutor Profile")),
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
                  labelText: "Subjects/skills taught",
                  hintText: "e.g. Java, DSA, Python",
                ),
                validator: (v) => (v == null || v.trim().isEmpty) ? "Enter at least one subject" : null,
              ),
              const SizedBox(height: 20),
              Text("Expertise level: $_expertiseLevel / 5", style: const TextStyle(fontWeight: FontWeight.bold)),
              Slider(
                value: _expertiseLevel.toDouble(),
                min: 1,
                max: 5,
                divisions: 4,
                label: "$_expertiseLevel",
                onChanged: (v) => setState(() => _expertiseLevel = v.round()),
              ),
              const SizedBox(height: 12),
              const Text("Teaching preference", style: TextStyle(fontWeight: FontWeight.bold)),
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
                    : const Text("Save Tutor Profile"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
