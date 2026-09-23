import 'package:flutter/material.dart';
import '../models/tutor.dart';
import '../services/api_service.dart';

class RecommendationScreen extends StatefulWidget {
  final int learnerId;

  const RecommendationScreen({super.key, required this.learnerId});

  @override
  State<RecommendationScreen> createState() => _RecommendationScreenState();
}

class _RecommendationScreenState extends State<RecommendationScreen> {
  late Future<List<TutorMatch>> _future;

  @override
  void initState() {
    super.initState();
    // All data here comes from the FastAPI backend — nothing is hardcoded.
    _future = ApiService.getRecommendations(widget.learnerId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Recommended Tutors")),
      body: FutureBuilder<List<TutorMatch>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Text("Could not load recommendations:\n${snapshot.error}",
                    textAlign: TextAlign.center),
              ),
            );
          }
          final matches = snapshot.data ?? [];
          if (matches.isEmpty) {
            return const Center(child: Text("No tutors found yet. Add some tutor profiles first."));
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: matches.length,
            separatorBuilder: (_, __) => const Divider(),
            itemBuilder: (context, index) {
              final m = matches[index];
              return Card(
                child: ListTile(
                  title: Text(m.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(
                    "${m.subjects.join(', ')}\n"
                    "${m.availability.join(', ')} • ${m.teachingPreference}",
                  ),
                  isThreeLine: true,
                  trailing: Text(
                    "${m.compatibilityScore.toStringAsFixed(0)}%",
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.green),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
