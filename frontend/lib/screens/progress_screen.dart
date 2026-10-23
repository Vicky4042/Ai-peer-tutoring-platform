import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ProgressScreen extends StatefulWidget {
  final int learnerId;
  const ProgressScreen({super.key, required this.learnerId});
  @override
  State<ProgressScreen> createState() => _ProgressScreenState();
}
class _ProgressScreenState extends State<ProgressScreen> {
  late Future<List<Map<String, dynamic>>> _future;
  late Future<Map<String, dynamic>> _summaryFuture;
  final _subject = TextEditingController();
  final _topic = TextEditingController();
  final _notes = TextEditingController();
  bool _completed = false;
  @override
  void initState() { super.initState(); _reload(); }
  void _reload() {
    _future = ApiService.getProgress(widget.learnerId);
    _summaryFuture = ApiService.getProgressSummary(widget.learnerId);
  }
  @override
  void dispose() { _subject.dispose(); _topic.dispose(); _notes.dispose(); super.dispose(); }
  Future<void> _add() async {
    if (_subject.text.trim().isEmpty || _topic.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter both subject and topic.'))); return;
    }
    try {
      await ApiService.addProgress({'learner_id': widget.learnerId, 'subject': _subject.text.trim(),
        'topic': _topic.text.trim(), 'notes': _notes.text.trim(), 'completed': _completed});
      _subject.clear(); _topic.clear(); _notes.clear(); _completed = false;
      setState(_reload);
    } catch (e) { if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e'))); }
  }
  @override
  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('My Learning Progress')),
    body: ListView(padding: const EdgeInsets.all(16), children: [
      Text('Learner ID: ${widget.learnerId}', style: Theme.of(context).textTheme.labelLarge),
      TextField(controller: _subject, decoration: const InputDecoration(labelText: 'Subject')),
      TextField(controller: _topic, decoration: const InputDecoration(labelText: 'Topic studied')),
      TextField(controller: _notes, decoration: const InputDecoration(labelText: 'Notes (optional)')),
      SwitchListTile(title: const Text('Mark topic completed'), value: _completed, onChanged: (v) => setState(() => _completed = v)),
      FilledButton.icon(onPressed: _add, icon: const Icon(Icons.add), label: const Text('Log progress')),
      const Divider(height: 32),
      FutureBuilder<Map<String, dynamic>>(
        future: _summaryFuture,
        builder: (context, snap) {
          if (snap.connectionState == ConnectionState.waiting) {
            return const Padding(padding: EdgeInsets.all(12), child: Center(child: CircularProgressIndicator()));
          }
          if (snap.hasError) {
            return Text('Progress summary unavailable: ${snap.error}');
          }
          final summary = snap.data ?? {};
          return Wrap(spacing: 8, runSpacing: 8, children: [
            _SummaryCard(label: 'Topics logged', value: '${summary['topics_logged'] ?? 0}', icon: Icons.menu_book),
            _SummaryCard(label: 'Topics completed', value: '${summary['topics_completed'] ?? 0}', icon: Icons.check_circle),
            _SummaryCard(label: 'Sessions completed', value: '${summary['sessions_completed'] ?? 0}', icon: Icons.event_available),
          ]);
        },
      ),
      const Divider(height: 32),
      FutureBuilder<List<Map<String, dynamic>>>(future: _future, builder: (context, snap) {
        if (snap.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
        if (snap.hasError) return Text('Could not load progress: ${snap.error}');
        final rows = snap.data ?? [];
        final done = rows.where((e) => e['completed'] == 1 || e['completed'] == true).length;
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Topics logged: ${rows.length}  •  Completed: $done', style: const TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          if (rows.isEmpty) const Text('No progress logged yet. Add your first topic above.'),
          ...rows.map((e) => Card(child: ListTile(leading: Icon((e['completed'] == 1 || e['completed'] == true) ? Icons.check_circle : Icons.menu_book),
            title: Text('${e['topic']}'), subtitle: Text('${e['subject']}\n${e['notes'] ?? ''}'))))
        ]);
      })
    ]));
}


class _SummaryCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  const _SummaryCard({required this.label, required this.value, required this.icon});

  @override
  Widget build(BuildContext context) => SizedBox(
    width: 155,
    child: Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Icon(icon, color: Theme.of(context).colorScheme.primary),
          const SizedBox(height: 8),
          Text(value, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
          Text(label),
        ]),
      ),
    ),
  );
}
