import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/learner.dart';
import '../models/tutor.dart';

/// All calls to the FastAPI backend go through this class.
class ApiService {
  // Chrome / web running on the same computer
  static const String baseUrl = "http://127.0.0.1:8000";

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
}