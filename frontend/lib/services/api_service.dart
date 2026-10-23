import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/learner.dart';
import '../models/tutor.dart';

/// All calls to the FastAPI backend go through this class.
class ApiService {
  // Chrome / web running on the same computer
  /// Override for Android emulator or another backend host with --dart-define=API_BASE_URL=...
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );

  static Future<Learner> createLearner(Learner learner) async {
    final response = await http.post(
      Uri.parse("$baseUrl/api/learners"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode(learner.toJson()),
    );

    if (response.statusCode == 201) {
      return Learner.fromJson(jsonDecode(response.body));
    }

    throw Exception(
      "Failed to create learner: ${response.statusCode} ${response.body}",
    );
  }

  static Future<Tutor> createTutor(Tutor tutor) async {
    final response = await http.post(
      Uri.parse("$baseUrl/api/tutors"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode(tutor.toJson()),
    );

    if (response.statusCode == 201) {
      return Tutor.fromJson(jsonDecode(response.body));
    }

    throw Exception(
      "Failed to create tutor: ${response.statusCode} ${response.body}",
    );
  }

  static Future<List<Tutor>> getTutors() async {
    final response = await http.get(
      Uri.parse("$baseUrl/api/tutors"),
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((t) => Tutor.fromJson(t)).toList();
    }

    throw Exception(
      "Failed to load tutors: ${response.statusCode}",
    );
  }

  static Future<List<TutorMatch>> getRecommendations(
      int learnerId) async {
    final response = await http.get(
      Uri.parse("$baseUrl/api/matches/$learnerId"),
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((t) => TutorMatch.fromJson(t)).toList();
    }

    throw Exception(
      "Failed to load recommendations: ${response.statusCode}",
    );
  }

  static Future<List<Map<String, dynamic>>> getResources({String subject = "all", String query = ""}) async {
    final uri = Uri.parse("$baseUrl/api/resources").replace(queryParameters: {
      if (subject.isNotEmpty) "subject": subject,
      if (query.trim().isNotEmpty) "q": query.trim(),
    });
    final response = await http.get(uri);
    if (response.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(response.body));
    }
    throw Exception("Failed to load learning materials: ${response.statusCode} ${response.body}");
  }

  static Future<Map<String, dynamic>> createSession(Map<String, dynamic> payload) async {
    final response = await http.post(Uri.parse("$baseUrl/api/sessions"),
      headers: {"Content-Type": "application/json"}, body: jsonEncode(payload));
    if (response.statusCode == 201) return Map<String, dynamic>.from(jsonDecode(response.body));
    throw Exception("Session request failed: ${response.statusCode} ${response.body}");
  }

  static Future<List<Map<String, dynamic>>> getSessions({int? learnerId, int? tutorId}) async {
    final uri = Uri.parse("$baseUrl/api/sessions").replace(queryParameters: {
      if (learnerId != null) "learner_id": "$learnerId",
      if (tutorId != null) "tutor_id": "$tutorId",
    });
    final response = await http.get(uri);
    if (response.statusCode == 200) return List<Map<String, dynamic>>.from(jsonDecode(response.body));
    throw Exception("Failed to load sessions: ${response.statusCode} ${response.body}");
  }

  static Future<Map<String, dynamic>> updateSession(int id, String status, {String responseText = ""}) async {
    final response = await http.patch(Uri.parse("$baseUrl/api/sessions/$id"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"status": status, "tutor_response": responseText}));
    if (response.statusCode == 200) return Map<String, dynamic>.from(jsonDecode(response.body));
    throw Exception("Session update failed: ${response.statusCode} ${response.body}");
  }

  static Future<List<Map<String, dynamic>>> getProgress(int learnerId) async {
    final response = await http.get(Uri.parse("$baseUrl/api/progress/$learnerId"));
    if (response.statusCode == 200) return List<Map<String, dynamic>>.from(jsonDecode(response.body));
    throw Exception("Failed to load progress: ${response.statusCode} ${response.body}");
  }

  static Future<Map<String, dynamic>> getProgressSummary(int learnerId) async {
    final response = await http.get(Uri.parse('$baseUrl/api/progress/$learnerId/summary'));
    if (response.statusCode == 200) {
      return Map<String, dynamic>.from(jsonDecode(response.body));
    }
    throw Exception('Failed to load progress summary: ${response.statusCode} ${response.body}');
  }

  static Future<Map<String, dynamic>> addProgress(Map<String, dynamic> payload) async {
    final response = await http.post(Uri.parse("$baseUrl/api/progress"),
      headers: {"Content-Type": "application/json"}, body: jsonEncode(payload));
    if (response.statusCode == 201) return Map<String, dynamic>.from(jsonDecode(response.body));
    throw Exception("Could not save progress: ${response.statusCode} ${response.body}");
  }

  static Future<Map<String, dynamic>> submitFeedback(int sessionId, Map<String, dynamic> payload) async {
    final response = await http.post(Uri.parse("$baseUrl/api/sessions/$sessionId/feedback"),
      headers: {"Content-Type": "application/json"}, body: jsonEncode(payload));
    if (response.statusCode == 201) return Map<String, dynamic>.from(jsonDecode(response.body));
    throw Exception("Could not submit feedback: ${response.statusCode} ${response.body}");
  }
}
