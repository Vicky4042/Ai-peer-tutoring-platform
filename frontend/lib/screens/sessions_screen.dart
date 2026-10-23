import 'package:flutter/material.dart';
import '../services/api_service.dart';

class SessionsScreen extends StatefulWidget {
  final int? learnerId;
  final int? tutorId;

  const SessionsScreen({
    super.key,
    this.learnerId,
    this.tutorId,
  });

  @override
  State<SessionsScreen> createState() => _SessionsScreenState();
}

class _SessionsScreenState extends State<SessionsScreen> {
  final _id = TextEditingController();
  String _role = 'learner';
  int? _activeId;
  late Future<List<Map<String, dynamic>>> _future;

  @override
  void initState() {
    super.initState();

    if (widget.tutorId != null) {
      _role = 'tutor';
      _activeId = widget.tutorId;
      _id.text = '${widget.tutorId}';
      _future = ApiService.getSessions(tutorId: widget.tutorId);
    } else if (widget.learnerId != null) {
      _role = 'learner';
      _activeId = widget.learnerId;
      _id.text = '${widget.learnerId}';
      _future = ApiService.getSessions(learnerId: widget.learnerId);
    } else {
      _future = Future.value([]);
    }
  }

  void _load() {
    final id = int.tryParse(_id.text.trim());

    if (id == null || id < 1) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Enter a valid numeric profile ID.'),
        ),
      );
      return;
    }

    setState(() {
      _activeId = id;
      _future = ApiService.getSessions(
        learnerId: _role == 'learner' ? id : null,
        tutorId: _role == 'tutor' ? id : null,
      );
    });
  }

  @override
  void dispose() {
    _id.dispose();
    super.dispose();
  }

  Future<void> _status(int sessionId, String status) async {
    try {
      await ApiService.updateSession(sessionId, status);

      if (!mounted) return;

      setState(() {
        _future = ApiService.getSessions(
          learnerId: _role == 'learner' ? _activeId : null,
          tutorId: _role == 'tutor' ? _activeId : null,
        );
      });
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tutoring Sessions'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(
                  value: 'learner',
                  label: Text('Learner'),
                ),
                ButtonSegment(
                  value: 'tutor',
                  label: Text('Tutor'),
                ),
              ],
              selected: {_role},
              onSelectionChanged: (v) {
                setState(() {
                  _role = v.first;
                  _activeId = null;
                });
              },
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _id,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Your profile ID',
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: _load,
                  child: const Text('Load'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Expanded(
              child: _activeId == null
                  ? const Center(
                      child: Text(
                        'Enter your learner or tutor profile ID '
                        'to view requests.',
                      ),
                    )
                  : FutureBuilder<List<Map<String, dynamic>>>(
                      future: _future,
                      builder: (context, snap) {
                        if (snap.connectionState ==
                            ConnectionState.waiting) {
                          return const Center(
                            child: CircularProgressIndicator(),
                          );
                        }

                        if (snap.hasError) {
                          return Center(
                            child: Text(
                              'Could not load sessions: ${snap.error}',
                            ),
                          );
                        }

                        final rows = snap.data ?? [];

                        if (rows.isEmpty) {
                          return const Center(
                            child: Text('No session requests yet.'),
                          );
                        }

                        return ListView.builder(
                          itemCount: rows.length,
                          itemBuilder: (context, i) {
                            final s = rows[i];
                            final status = '${s['status']}';

                            return Card(
                              child: Padding(
                                padding: const EdgeInsets.all(12),
                                child: Column(
                                  crossAxisAlignment:
                                      CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      '${s['subject']} • ${s['topic']}',
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 16,
                                      ),
                                    ),
                                    Text(
                                      'Session #${s['id']} • '
                                      '${s['scheduled_at']}',
                                    ),
                                    Text(
                                      'Learner #${s['learner_id']} • '
                                      'Tutor #${s['tutor_id']}',
                                    ),
                                    Text(
                                      'Status: ${status.toUpperCase()}',
                                    ),
                                    if ('${s['message']}'.isNotEmpty)
                                      Text('Message: ${s['message']}'),
                                    if ('${s['tutor_response']}'.isNotEmpty)
                                      Text(
                                        'Response: ${s['tutor_response']}',
                                      ),
                                    if (_role == 'tutor' &&
                                        status == 'pending')
                                      Wrap(
                                        spacing: 8,
                                        children: [
                                          TextButton(
                                            onPressed: () => _status(
                                              s['id'] as int,
                                              'accepted',
                                            ),
                                            child: const Text('Accept'),
                                          ),
                                          TextButton(
                                            onPressed: () => _status(
                                              s['id'] as int,
                                              'rejected',
                                            ),
                                            child: const Text('Reject'),
                                          ),
                                        ],
                                      ),
                                    if (_role == 'tutor' &&
                                        status == 'accepted')
                                      TextButton(
                                        onPressed: () => _status(
                                          s['id'] as int,
                                          'completed',
                                        ),
                                        child: const Text('Mark completed'),
                                      ),
                                    if (_role == 'learner' &&
                                        (status == 'pending' ||
                                            status == 'accepted'))
                                      TextButton(
                                        onPressed: () => _status(
                                          s['id'] as int,
                                          'cancelled',
                                        ),
                                        child: const Text('Cancel request'),
                                      ),
                                    if (_role == 'learner' &&
                                        status == 'completed')
                                      _FeedbackForm(
                                        sessionId: s['id'] as int,
                                        learnerId: s['learner_id'] as int,
                                      ),
                                  ],
                                ),
                              ),
                            );
                          },
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

class _FeedbackForm extends StatefulWidget {
  final int sessionId;
  final int learnerId;

  const _FeedbackForm({
    required this.sessionId,
    required this.learnerId,
  });

  @override
  State<_FeedbackForm> createState() => _FeedbackFormState();
}

class _FeedbackFormState extends State<_FeedbackForm> {
  int _rating = 5;
  final _comment = TextEditingController();
  bool _sent = false;

  @override
  void dispose() {
    _comment.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_sent) {
      return const Text('Feedback submitted');
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Rate this session'),
        DropdownButton<int>(
          value: _rating,
          items: [1, 2, 3, 4, 5]
              .map(
                (n) => DropdownMenuItem<int>(
                  value: n,
                  child: Text('$n / 5'),
                ),
              )
              .toList(),
          onChanged: (v) {
            if (v != null) {
              setState(() => _rating = v);
            }
          },
        ),
        TextField(
          controller: _comment,
          decoration: const InputDecoration(
            labelText: 'Feedback (optional)',
          ),
        ),
        TextButton(
          onPressed: () async {
            try {
              await ApiService.submitFeedback(
                widget.sessionId,
                {
                  'learner_id': widget.learnerId,
                  'rating': _rating,
                  'comment': _comment.text.trim(),
                },
              );

              if (!mounted) return;

              setState(() => _sent = true);
            } catch (e) {
              if (!mounted) return;

              ScaffoldMessenger.of(this.context).showSnackBar(
                SnackBar(content: Text('$e')),
              );
            }
          },
          child: const Text('Submit feedback'),
        ),
      ],
    );
  }
}
