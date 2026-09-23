class Tutor {
  final int? id;
  final String name;
  final String email;
  final List<String> subjects;
  final int expertiseLevel;
  final String teachingPreference;
  final List<String> availability;

  Tutor({
    this.id,
    required this.name,
    required this.email,
    required this.subjects,
    required this.expertiseLevel,
    required this.teachingPreference,
    required this.availability,
  });

  Map<String, dynamic> toJson() => {
        "name": name,
        "email": email,
        "subjects": subjects,
        "expertise_level": expertiseLevel,
        "teaching_preference": teachingPreference,
        "availability": availability,
      };

  factory Tutor.fromJson(Map<String, dynamic> json) => Tutor(
        id: json["id"],
        name: json["name"],
        email: json["email"],
        subjects: List<String>.from(json["subjects"] ?? []),
        expertiseLevel: json["expertise_level"],
        teachingPreference: json["teaching_preference"],
        availability: List<String>.from(json["availability"] ?? []),
      );
}

/// Result item returned by GET /api/matches/{learner_id}.
/// This is a ranked tutor + its compatibility score — NOT a plain Tutor.
class TutorMatch {
  final int tutorId;
  final String name;
  final List<String> subjects;
  final String teachingPreference;
  final List<String> availability;
  final double compatibilityScore;

  TutorMatch({
    required this.tutorId,
    required this.name,
    required this.subjects,
    required this.teachingPreference,
    required this.availability,
    required this.compatibilityScore,
  });

  factory TutorMatch.fromJson(Map<String, dynamic> json) => TutorMatch(
        tutorId: json["tutor_id"],
        name: json["name"],
        subjects: List<String>.from(json["subjects"] ?? []),
        teachingPreference: json["teaching_preference"],
        availability: List<String>.from(json["availability"] ?? []),
        compatibilityScore: (json["compatibility_score"] as num).toDouble(),
      );
}
