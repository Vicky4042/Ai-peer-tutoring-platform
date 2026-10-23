
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';

class LearningMaterialsScreen extends StatefulWidget {
  const LearningMaterialsScreen({super.key});

  @override
  State<LearningMaterialsScreen> createState() =>
      _LearningMaterialsScreenState();
}

class _LearningMaterialsScreenState extends State<LearningMaterialsScreen> {
  final _search = TextEditingController();
  String _subject = 'all';
  late Future<List<Map<String, dynamic>>> _future;

  final _subjects = const [
    'all',
    'Python',
    'Java',
    'JavaScript',
    'SQL',
    'Git',
    'Flutter',
    'Computer Science',
    'Data Structures',
    'Web Development'
  ];

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() {
    _future = ApiService.getResources(
      subject: _subject,
      query: _search.text,
    );
  }

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Learning Materials')),
        body: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              TextField(
                controller: _search,
                decoration: InputDecoration(
                  labelText: 'Search materials',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.search),
                    onPressed: () => setState(_load),
                  ),
                ),
                onSubmitted: (_) => setState(_load),
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                initialValue: _subject,
                decoration: const InputDecoration(
                  labelText: 'Filter by subject',
                ),
                items: _subjects
                    .map(
                      (s) => DropdownMenuItem(
                        value: s,
                        child: Text(s == 'all' ? 'All subjects' : s),
                      ),
                    )
                    .toList(),
                onChanged: (v) {
                  if (v != null) {
                    setState(() {
                      _subject = v;
                      _load();
                    });
                  }
                },
              ),
              const SizedBox(height: 12),
              Expanded(
                child: FutureBuilder<List<Map<String, dynamic>>>(
                  future: _future,
                  builder: (context, snap) {
                    if (snap.connectionState == ConnectionState.waiting) {
                      return const Center(
                        child: CircularProgressIndicator(),
                      );
                    }

                    if (snap.hasError) {
                      return Center(
                        child: Text(
                          'Could not load resources. Check that the backend is running.\n${snap.error}',
                          textAlign: TextAlign.center,
                        ),
                      );
                    }

                    final rows = snap.data ?? [];

                    if (rows.isEmpty) {
                      return const Center(
                        child: Text('No materials match this filter.'),
                      );
                    }

                    return ListView.separated(
                      itemCount: rows.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 6),
                      itemBuilder: (context, i) {
                        final r = rows[i];

                        return Card(
                          child: ListTile(
                            leading: const CircleAvatar(
                              child: Icon(Icons.menu_book),
                            ),
                            title: Text(
                              '${r['title'] ?? 'Learning resource'}',
                            ),
                            subtitle: Text(
                              '${r['subject']} • ${r['resource_type']}\n${r['description'] ?? ''}',
                            ),
                            isThreeLine: true,
                            trailing: const Icon(Icons.open_in_new),
                            onTap: () async {
                              final uri = Uri.tryParse('${r['url']}');

                              if (uri == null ||
                                  !(uri.scheme == 'https' ||
                                      uri.scheme == 'http')) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text(
                                      'This resource URL is invalid.',
                                    ),
                                  ),
                                );
                                return;
                              }

                              final opened = await launchUrl(
                                uri,
                                mode: LaunchMode.externalApplication,
                              );

                              if (!opened && context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text(
                                      'Could not open link. Copy it from the resource details.',
                                    ),
                                  ),
                                );
                              }
                            },
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
