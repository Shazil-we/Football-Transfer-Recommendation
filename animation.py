from manim import *
import random

class FootballScoutViz(Scene):
    def construct(self):
        # --- CONFIGURATION ---
        col_bg = "#1e1e24"
        col_arsenal = "#EF0107"
        col_world = "#A0A0B0"
        col_match = "#00D084"
        col_gold = "#FFD700"
        col_cluster_1 = "#3498db" # Blue for CB
        col_cluster_2 = "#e67e22" # Orange for FB
        
        self.camera.background_color = col_bg

        # ==========================================
        # SCENE 1: INTRO
        # ==========================================
        self.main_title = Text("Moneyball Transfer Scout", font_size=60, weight=BOLD, color=WHITE)
        subtitle = Text("From Raw Data to Transfer Targets", font_size=24, color=col_match)
        subtitle.next_to(self.main_title, DOWN)

        self.play(Write(self.main_title))
        self.play(FadeIn(subtitle, shift=UP))
        self.wait(1)
        
        # Transition title to top left and keep it there for now
        self.play(
            self.main_title.animate.scale(0.4).to_corner(UL),
            FadeOut(subtitle)
        )

        # ==========================================
        # SCENE 2: DATA CLEANING & K-MEANS
        # ==========================================
        
        # 1. Raw Data Cloud
        step1_text = Text("Step 1: Preprocessing", font_size=30, color=GREY).to_edge(UP)
        self.play(Write(step1_text))

        raw_dots = VGroup()
        for _ in range(60):
            x = random.uniform(-6, 6)
            y = random.uniform(-3, 3)
            dot = Dot(point=[x, y, 0], color=col_world, radius=0.06)
            raw_dots.add(dot)
            
        self.play(LaggedStart([FadeIn(d) for d in raw_dots], run_time=2, lag_ratio=0.05))
        
        # 2. Filtering (Remove players with < 5.0 90s)
        filter_text = Text("Filtering: Removing players < 5.0 90s", font_size=24, color=RED).next_to(step1_text, DOWN)
        self.play(Write(filter_text))
        
        # Randomly select dots to "filter out"
        dots_to_remove = [raw_dots[i] for i in range(0, 60, 3)] # Remove every 3rd
        remaining_dots = [d for d in raw_dots if d not in dots_to_remove]
        
        self.play(
            [FadeOut(d, scale=0.1) for d in dots_to_remove],
            run_time=1
        )
        self.play(FadeOut(filter_text))

        # 3. K-Means Clustering Animation
        step2_text = Text("Step 2: K-Means Clustering (Defining SubRoles)", font_size=30, color=GREY).to_edge(UP)
        self.play(Transform(step1_text, step2_text))

        # Move dots into two distinct clusters
        cluster_cb = VGroup() # Left cluster
        cluster_fb = VGroup() # Right cluster

        anims = []
        
        for dot in remaining_dots:
            # Randomly assign to cluster A or B
            if random.random() > 0.5:
                target_x = random.uniform(-5, -1)
                target_y = random.uniform(-2, 2)
                anims.append(dot.animate.move_to([target_x, target_y, 0]).set_color(col_cluster_1))
                cluster_cb.add(dot)
            else:
                target_x = random.uniform(1, 5)
                target_y = random.uniform(-2, 2)
                anims.append(dot.animate.move_to([target_x, target_y, 0]).set_color(col_cluster_2))
                cluster_fb.add(dot)

        self.play(*anims, run_time=2)

        # Label the Clusters
        label_cb = Text("Center Backs", font_size=20, color=col_cluster_1).next_to(cluster_cb, UP)
        label_fb = Text("Full Backs", font_size=20, color=col_cluster_2).next_to(cluster_fb, UP)

        self.play(Write(label_cb), Write(label_fb))
        self.wait(1)

        # Transition: Focus on one subrole (e.g., Selecting WINGERS for next step)
        self.play(
            FadeOut(cluster_cb), FadeOut(label_cb),
            FadeOut(cluster_fb), FadeOut(label_fb),
            FadeOut(step1_text) # Removes the "Step 2" text
        )

        # ==========================================
        # SCENE 3: THE SCOUTING ALGORITHM
        # ==========================================
        
        # Setup Graph
        step3_text = Text("Step 3: Similarity Search (Wingers)", font_size=30, color=GREY).to_edge(UP)
        self.play(Write(step3_text))

        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=7,
            y_length=5,
            axis_config={"color": GREY},
            tips=False
        ).to_edge(LEFT, buff=1).shift(DOWN*0.5)
        
        x_label = Text("Progressive Carries", font_size=18).next_to(axes.x_axis, DOWN)
        y_label = Text("Key Passes / 90", font_size=18).next_to(axes.y_axis, LEFT).rotate(90 * DEGREES)

        self.play(Create(axes), Write(x_label), Write(y_label))

        # 1. Generate "World" Players
        world_dots = VGroup()
        for _ in range(30):
            x = random.uniform(1, 9)
            y = random.uniform(1, 9)
            dot = Dot(axes.c2p(x, y), color=col_world, radius=0.05)
            world_dots.add(dot)

        # 2. Generate "Club" Players (Red)
        club_dots = VGroup()
        club_coords = [(6, 7), (6.5, 6.8), (7, 7.5), (5.8, 7.2), (6.2, 8)]
        for x, y in club_coords:
            dot = Dot(axes.c2p(x, y), color=col_arsenal, radius=0.1)
            club_dots.add(dot)

        self.play(LaggedStart([FadeIn(d, scale=0.5) for d in world_dots], run_time=1))
        self.play(LaggedStart([DrawBorderThenFill(d) for d in club_dots], run_time=0.5))
        
        club_label = Text("Current Squad", font_size=20, color=col_arsenal).next_to(club_dots, UP)
        self.play(Write(club_label))

        # 3. Centroid Calculation
        avg_x = sum([c[0] for c in club_coords]) / len(club_coords)
        avg_y = sum([c[1] for c in club_coords]) / len(club_coords)
        centroid_point = axes.c2p(avg_x, avg_y)
        
        centroid_dot = Dot(centroid_point, color=col_gold, radius=0.15)
        centroid_glow = Dot(centroid_point, color=col_gold, radius=0.3).set_opacity(0.3)
        centroid_text = Text("Club DNA", font_size=20, color=col_gold).next_to(centroid_dot, RIGHT)

        self.play(
            ReplacementTransform(club_dots, centroid_dot),
            FadeIn(centroid_glow),
            FadeOut(club_label)
        )
        self.play(Write(centroid_text))

        # 4. Finding the Target
        target_coord = (6.8, 7.8)
        target_point = axes.c2p(*target_coord)
        target_dot = Dot(target_point, color=col_match, radius=0.15)
        
        self.play(Transform(world_dots[15], target_dot))
        target_label = Text("Target: A. Traoré", font_size=20, color=col_match).next_to(target_dot, LEFT)
        self.play(Write(target_label))

        # 5. Vectors & Math
        origin = axes.c2p(0, 0)
        vec_dna = Arrow(origin, centroid_point, buff=0, color=col_gold, stroke_width=3)
        vec_target = Arrow(origin, target_point, buff=0, color=col_match, stroke_width=3)

        self.play(GrowArrow(vec_dna), GrowArrow(vec_target))

        # Angle
        angle = Angle(vec_dna, vec_target, radius=0.6, color=WHITE)
        angle_label = Text("θ", font_size=20).next_to(angle, UP)
        
        # Text Formula (No LaTeX)
        cos_formula = Text("Similarity = cos(θ)", font_size=24, color=WHITE)
        cos_formula.to_corner(UR).shift(DOWN*1.5)

        self.play(Create(angle), Write(angle_label))
        self.play(Write(cos_formula))
        
        # Distance Line
        dist_line = DashedLine(centroid_point, target_point, color=WHITE)
        dist_formula = Text("Distance (Euclidean)", font_size=24, color=WHITE)
        dist_formula.next_to(cos_formula, DOWN, buff=0.3)

        self.play(Create(dist_line))
        self.play(Write(dist_formula))
        self.wait(1)

        # Score Result
        score = Text("Match: 94%", font_size=40, weight=BOLD, color=col_match)
        score.move_to(axes.c2p(8, 2))
        self.play(TransformFromCopy(dist_line, score))
        self.wait(2)

        # ==========================================
        # SCENE 4: THE RESULTS (Fixing Overlap)
        # ==========================================
        
        # 1. Explicitly Fade Out everything currently on screen
        # We group everything we added + the Main Title from Scene 1
        self.play(
            FadeOut(axes), FadeOut(world_dots), FadeOut(vec_dna), 
            FadeOut(vec_target), FadeOut(angle), FadeOut(angle_label),
            FadeOut(centroid_dot), FadeOut(centroid_glow), FadeOut(target_dot),
            FadeOut(target_label), FadeOut(centroid_text), FadeOut(x_label), 
            FadeOut(y_label), FadeOut(dist_line), FadeOut(cos_formula), 
            FadeOut(dist_formula), FadeOut(score), FadeOut(step3_text),
            FadeOut(self.main_title) # <--- IMPORTANT: Removes the top-left title
        )

        # 2. Create Final Table
        header = Text("Top Recommendations (WINGER)", font_size=36, weight=BOLD, color=WHITE).to_edge(UP)
        
        # Data
        rows = [
            ["1. Adama Traoré", "Fulham", "94%"],
            ["2. Bryan Zaragoza", "Osasuna", "89%"],
            ["3. David Neres", "Napoli", "87%"],
            ["4. Moses Simon", "Nantes", "86%"],
        ]

        table_group = VGroup()
        for i, row_data in enumerate(rows):
            # Manual table layout using Text objects
            t_name = Text(row_data[0], font_size=28, color=WHITE).to_edge(LEFT, buff=3)
            t_club = Text(row_data[1], font_size=28, color=GREY_B).next_to(t_name, RIGHT, buff=1.5)
            t_score = Text(row_data[2], font_size=28, weight=BOLD, color=col_match).to_edge(RIGHT, buff=3)
            
            row_group = VGroup(t_name, t_club, t_score)
            row_group.shift(UP * (1.5 - i * 1)) # Spacing rows
            
            # Underline
            line = Line(start=row_group.get_left(), end=row_group.get_right(), color=GREY, stroke_width=1)
            line.next_to(row_group, DOWN, buff=0.2)
            
            table_group.add(row_group, line)

        self.play(Write(header))
        self.play(LaggedStart(
            [FadeIn(r, shift=RIGHT) for r in table_group],
            run_time=2, lag_ratio=0.3
        ))

        self.wait(3)
        self.play(FadeOut(header), FadeOut(table_group))