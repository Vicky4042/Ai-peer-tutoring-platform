
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
                padding: const EdgeInsets.all(24),
                child: Text(
                  "Could not load recommendations:\n${snapshot.error}",
                  textAlign: TextAlign.center,
                ),
              ),
            );
          }

          final matches = snapshot.data ?? [];

          if (matches.isEmpty) {
            return const Center(
              child: Text(
                "No tutors found yet. Add some tutor profiles first.",
              ),
            );
          }

          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: matches.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final m = matches[index];

              final isMl = m.scoringMethod.toLowerCase() == 'ml';
              final sourceLabel = isMl ? 'ML recommendation' : 'Fallback scorer';
              final sourceColor = isMl ? Colors.blue : Colors.orange;

              return Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              m.name,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 17,
                              ),
                            ),
                          ),
                          Text(
                            '${m.matchScore.toStringAsFixed(1)}%',
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.green,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 6,
                        runSpacing: 6,
                        children: [
                          Chip(
                            avatar: Icon(
                              isMl ? Icons.auto_awesome : Icons.rule,
                              size: 16,
                              color: sourceColor,
                            ),
                            label: Text(sourceLabel),
                            visualDensity: VisualDensity.compact,
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text('Subjects: ${m.subjects.join(', ')}'),
                      const SizedBox(height: 4),
                      Text('Availability: ${m.availability.join(', ')}'),
                      const SizedBox(height: 4),
                      Text('Teaching preference: ${m.teachingPreference}'),

                      if (isMl && m.mlMatchProbability != null) ...[
                        const SizedBox(height: 8),
                        Text(
                          'ML probability: '
                          '${(m.mlMatchProbability! * 100).toStringAsFixed(1)}%',
                          style: TextStyle(
                            color: Colors.grey.shade700,
                            fontSize: 12,
                          ),
                        ),
                      ],

                      if (!isMl &&
                          m.fallbackReason != null &&
                          m.fallbackReason!.trim().isNotEmpty) ...[
                        const SizedBox(height: 8),
                        Text(
                          'Fallback reason: ${m.fallbackReason}',
                          style: TextStyle(
                            color: Colors.grey.shade700,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ],
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
