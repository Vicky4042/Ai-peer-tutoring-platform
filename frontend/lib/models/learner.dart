class Learner {
  final int? id;
  final String name;
  final String email;
  final List<String> subjects;
  final String learningPreference;
  final List<String> availability;

  Learner({
    this.id,
    required this.name,
    required this.email,
    required this.subjects,
    required this.learningPreference,
    required this.availability,
  });

  Map<String, dynamic> toJson() => {
        "name": name,
        "email": email,
        "subjects": subjects,
        "learning_preference": learningPreference,
        "availability": availability,
      };

  factory Learner.fromJson(Map<String, dynamic> json) => Learner(
        id: json["id"],
        name: json["name"],
        email: json["email"],
        subjects: List<String>.from(json["subjects"] ?? []),
        learningPreference: json["learning_preference"],
        availability: List<String>.from(json["availability"] ?? []),
      );
}
