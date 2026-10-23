

import 'package:flutter/material.dart';
import '../models/tutor.dart';
import '../services/api_service.dart';
import 'learning_materials_screen.dart';
import 'progress_screen.dart';
import 'sessions_screen.dart';

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

  Future<void> _requestSession(TutorMatch tutor) async {
    final topic = TextEditingController();
    final message = TextEditingController();

    DateTime scheduled = DateTime.now().add(const Duration(days: 1));

    final subjectOptions = tutor.matchedSubjects.isNotEmpty
        ? tutor.matchedSubjects
        : tutor.subjects;

    String? subject =
        subjectOptions.isEmpty ? null : subjectOptions.first;

    try {
      final result = await showDialog<bool>(
        context: context,
        builder: (dialogContext) => StatefulBuilder(
          builder: (context, setDialogState) => AlertDialog(
            title: Text('Request session with ${tutor.name}'),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  DropdownButtonFormField<String>(
                    initialValue: subject,
                    decoration: const InputDecoration(
                      labelText: 'Subject',
                    ),
                    items: subjectOptions
                        .map(
                          (s) => DropdownMenuItem<String>(
                            value: s,
                            child: Text(s),
                          ),
                        )
                        .toList(),
                    onChanged: (v) =>
                        setDialogState(() => subject = v),
                  ),
                  TextField(
                    controller: topic,
                    decoration: const InputDecoration(
                      labelText: 'Topic to learn',
                    ),
                  ),
                  TextField(
                    controller: message,
                    decoration: const InputDecoration(
                      labelText: 'Message (optional)',
                    ),
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    icon: const Icon(Icons.calendar_today),
                    label: Text(
                      '${scheduled.year}-'
                      '${scheduled.month.toString().padLeft(2, '0')}-'
                      '${scheduled.day.toString().padLeft(2, '0')}',
                    ),
                    onPressed: () async {
                      final d = await showDatePicker(
                        context: context,
                        initialDate: scheduled,
                        firstDate: DateTime.now(),
                        lastDate: DateTime.now().add(
                          const Duration(days: 180),
                        ),
                      );

                      if (d != null) {
                        setDialogState(() {
                          scheduled = DateTime(
                            d.year,
                            d.month,
                            d.day,
                            scheduled.hour,
                            scheduled.minute,
                          );
                        });
                      }
                    },
                  ),
                  OutlinedButton.icon(
                    icon: const Icon(Icons.access_time),
                    label: Text(
                      '${scheduled.hour.toString().padLeft(2, '0')}:'
                      '${scheduled.minute.toString().padLeft(2, '0')}',
                    ),
                    onPressed: () async {
                      final t = await showTimePicker(
                        context: context,
                        initialTime: TimeOfDay.fromDateTime(scheduled),
                      );

                      if (t != null) {
                        setDialogState(() {
                          scheduled = DateTime(
                            scheduled.year,
                            scheduled.month,
                            scheduled.day,
                            t.hour,
                            t.minute,
                          );
                        });
                      }
                    },
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(dialogContext, false),
                child: const Text('Cancel'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(dialogContext, true),
                child: const Text('Send request'),
              ),
            ],
          ),
        ),
      );

      if (result != true || !mounted) return;

      if (topic.text.trim().length < 2 || subject == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Enter a topic and select a subject.'),
          ),
        );
        return;
      }

      try {
        await ApiService.createSession({
          'learner_id': widget.learnerId,
          'tutor_id': tutor.tutorId,
          'subject': subject,
          'topic': topic.text.trim(),
          'scheduled_at': scheduled.toIso8601String(),
          'message': message.text.trim(),
        });

        if (!mounted) return;

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Session request sent. Open Sessions to track its status.',
            ),
          ),
        );
      } catch (e) {
        if (!mounted) return;

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$e')),
        );
      }
    } finally {
      topic.dispose();
      message.dispose();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Recommended Tutors'),
        actions: [
          IconButton(
            tooltip: 'Learning materials',
            icon: const Icon(Icons.menu_book),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => const LearningMaterialsScreen(),
              ),
            ),
          ),
          IconButton(
            tooltip: 'My progress',
            icon: const Icon(Icons.trending_up),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ProgressScreen(
                  learnerId: widget.learnerId,
                ),
              ),
            ),
          ),
          IconButton(
            tooltip: 'Sessions',
            icon: const Icon(Icons.event),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => SessionsScreen(
                  learnerId: widget.learnerId,
                ),
              ),
            ),
          ),
        ],
      ),
      body: FutureBuilder<List<TutorMatch>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Text(
                  'Could not load recommendations:\n${snapshot.error}',
                  textAlign: TextAlign.center,
                ),
              ),
            );
          }

          final matches = snapshot.data ?? [];

          if (matches.isEmpty) {
            return const Center(
              child: Text(
                'No tutors found yet. Add some tutor profiles first.',
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
              final sourceLabel =
                  isMl ? 'ML recommendation' : 'Fallback scorer';
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
                      Text(
                        'Availability: ${m.availability.join(', ')}',
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Teaching preference: ${m.teachingPreference}',
                      ),
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
                      const SizedBox(height: 8),
                      Align(
                        alignment: Alignment.centerRight,
                        child: FilledButton.icon(
                          onPressed: () => _requestSession(m),
                          icon: const Icon(Icons.calendar_month),
                          label: const Text('Request session'),
                        ),
                      ),
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
