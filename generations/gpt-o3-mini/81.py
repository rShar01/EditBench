from ast import Add
from asyncio import wait
from curses import COLOR_BLUE, COLOR_RED
from re import A
from shutil import move
from glm import degrees
from manim import *
from numpy import size, square

class Project(Scene):
    def construct(self):
        text = Tex("Double Angle")
        self.play(Write(text))

        self.wait(5)
 
        transform_text = Tex("What is Double Angle?")
        transform_text.to_corner(UP)
        box = SurroundingRectangle(transform_text)
        box.set_color(WHITE)
        box.set_stroke(width=1.5)
        self.play(
            Transform(text, transform_text)
        )
        self.wait(0.5)
        self.play(Create(box))

        explanation = Paragraph("A double angle is an angle measurement", "that has been multiplied by 2 or added to itself.", line_spacing=0.5, font_size=32)
        explanation.move_to(ORIGIN)

        self.play(
            Write(explanation)
        )
        self.wait(3)
        self.play(
            Transform(explanation, explanation.copy().shift(UP))
        )

        trig_cos2 = MathTex(
            r"\cos2x = \cos^2x - \sin^2x",
            substrings_to_isolate=["cos2x"]
        )
        trig_cos2.set_color_by_tex("cos2x", BLUE)
        trig_cos2.move_to(DOWN)
        transform_formula = Tex("Double Angle Formula")
        transform_formula.to_corner(UP)
       
        self.wait(1)
        self.play(
            Write(trig_cos2)
        )
        self.wait(2)
        self.play(
            FadeOut(trig_cos2, explanation)
        )
        self.wait(1)

        axes = Axes(
            x_range=[-2, 2, 2],
            y_range=[-2, 2, 2],
            x_length=4,
            y_length=4,
        )
        self.add(axes)

        # 単位円の作成
        circle = Circle(radius=2, color=BLUE)
        self.add(circle)

        # 原点 (Origin)
        dot = Dot(ORIGIN, color=RED)
        self.add(dot)

        # 角度を表す線分 (Line representing the angle)
        line = Line(ORIGIN, RIGHT * 2)
        self.add(line)

        # 角度のラベル (Angle label)
        # Create an Arc for the angle
        angle = Arc(
            radius=2,
            start_angle=0,  # Start at the positive x-axis
            angle=line.get_angle(),  # Use line's angle
            arc_center=ORIGIN,
            color=GREEN
        )
        angle_label = MathTex(r"\theta = 0^{\circ}").next_to(angle, RIGHT)  # Changed Tex to MathTex and added \\
        self.add(angle, angle_label)

        intersection_dot = Dot(color=YELLOW)

        angle_tracker = ValueTracker(0)

        def update_line(mobject):
            mobject.become(Line(ORIGIN, RIGHT * 2).rotate(angle_tracker.get_value(), about_point=ORIGIN))

        def update_angle(mobject):
            mobject.become(Arc(
                radius=2,
                start_angle=0,
                angle=angle_tracker.get_value(),
                arc_center=ORIGIN,
                color=GREEN
            ))

        line.add_updater(update_line)
        angle.add_updater(update_angle)

        # Update the angle label
        def update_label(mobject):
            angle_in_degrees = np.degrees(angle_tracker.get_value())
            mobject.become(MathTex(rf"\theta = {angle_in_degrees:.0f}^{{\circ}}"))
            mobject.next_to(angle, RIGHT)

        angle_label.add_updater(update_label)

        def update_intersection_dot(mobject):
            angle_val = angle_tracker.get_value()
            x = 2 * np.cos(angle_val)  # x-coordinate on the circle
            y = 2 * np.sin(angle_val)  # y-coordinate on the circle
            mobject.move_to([x, y, 0])

        intersection_dot.add_updater(update_intersection_dot)

        self.add(intersection_dot)
        # Animate the angle
        self.play(
            angle_tracker.animate.set_value(PI / 6),
            run_time=2
        )
        self.wait(3)

        line.clear_updaters()
        intersection_dot.clear_updaters()
        angle.clear_updaters()
        angle_label.clear_updaters()

        # Change their color to indicate they are fixed
        fixed_line = line.copy().set_color(ORANGE)
        fixed_dot = intersection_dot.copy().set_color(ORANGE)
        fixed_angle = angle.copy().set_color(ORANGE)
        self.add(fixed_line, fixed_dot, fixed_angle)

        # Prepare a new line for the next animation
        new_line = Line(ORIGIN, RIGHT * 2, color=GREEN)
        new_intersection_dot = Dot(color=YELLOW)
        new_angle = Arc(
            radius=0.5,
            start_angle=PI / 6,  # Start from 30 degrees
            angle=0,
            arc_center=ORIGIN,
            color=GREEN
        )
        new_label = MathTex(rf"\theta = 30^\circ").next_to(new_angle, RIGHT).set_color(ORANGE)

        # Updaters for the new objects
        new_line.add_updater(lambda m: m.become(
            Line(ORIGIN, RIGHT * 2).rotate(angle_tracker.get_value(), about_point=ORIGIN)
        ))

        new_intersection_dot.add_updater(lambda m: m.move_to([
            2 * np.cos(angle_tracker.get_value()),
            2 * np.sin(angle_tracker.get_value()),
            0
        ]))

        new_angle.add_updater(lambda m: m.become(
            Arc(
                radius=0.5,
                start_angle=0,
                angle=angle_tracker.get_value(),
                arc_center=ORIGIN,
                color=GREEN
            )
        ))

        new_label.add_updater(lambda m: m.become(
            MathTex(rf"\theta = {np.degrees(angle_tracker.get_value()):.0f}^\circ").next_to(new_angle, LEFT)
        ))

        # Add the new objects
        self.add(new_line, new_intersection_dot, new_angle, new_label)

        # Animate from 30 degrees to 60 degrees
        self.play(
            angle_tracker.animate.set_value(PI / 3),  # 60 degrees
            run_time=2
        )
        self.wait(1)
        self.wait(10)

        self.play(
            FadeOut(circle, dot, line, angle, angle_label, axes, line, angle, intersection_dot, angle_label, new_line, new_angle, new_label, new_intersection_dot, fixed_line, fixed_angle, fixed_dot, angle_tracker)
        )

        self.play(
            FadeOut(transform_text, explanation),
            Transform(trig_cos2 , trig_cos2.copy().shift(UP + UP + UP)),
            Transform(text, transform_formula),
        )
        self.wait(2)

        cos_xx = MathTex(
            r"\cos2x = \cos(A+B)"
        )
        cos_xx.move_to(ORIGIN + UP)

        cos_ab = MathTex(
            r"\cos(A+B) =(\cos A \cdot \cos B) - (\sin A \cdot \sin B)"
        )
        cos_ab.move_to(ORIGIN)

        let_AB = Tex("Let A = B")
        let_AB.move_to(ORIGIN + DOWN)

        ab_simple = MathTex(
            r"\cos(A+A) = \cos^2A - \sin^2A"
        )
        ab_simple.move_to(ORIGIN + DOWN + DOWN)

        ab_finalize = MathTex(
            r"= 1-2\sin^2x"
        )
        ab_finalize.move_to(ORIGIN + DOWN + DOWN + DOWN + RIGHT)

        self.play(
            Write(cos_xx)
        )
        self.wait(0.5)
        self.play(
            Write(cos_ab),
        )
        self.wait(0.5)
        self.play(
            Write(let_AB)
        )
        self.wait(0.5)
        self.play(
            Write(ab_simple)
        )
        self.wait(0.5)
        self.play(
            Write(ab_finalize)
        )
       
        arrow = Arrow(2*UP, 2*DOWN)
        VGroup(arrow).set_x(0).arrange(buff=2)
        arrow.move_to(ORIGIN + RIGHT + RIGHT + RIGHT + RIGHT + RIGHT + RIGHT)
        self.play(Write(arrow))
       
        self.wait(15)

        self.play(
            FadeOut(text, transform_text, trig_cos2, cos_xx, cos_ab, let_AB, ab_simple, ab_finalize, arrow, box, transform_formula)
        )
        self.wait(1)
        #moving to the explanation of example

        #What is proof in Math?
        proof = Tex("What is proof?", font_size=48)
        self.play(Write(proof))
        self.wait(3)

        self.play(
            Transform(proof, proof.copy().shift(UP).shift(UP))
        )

        proof_exp = Paragraph("In trigonometry, a proof is a way to show that ", "two trigonometric expressions are equivalent, regardless of the angle. ", "This process is called validating or proving trigonometric identities.", font_size=28)
        self.play(Write(proof_exp))
        self.wait(8)
        self.play(
            FadeOut(proof, proof_exp)
        )

        #starting with Sin and Cos graph identity

        ax = Axes()
        sine = ax.plot(np.sin, color=RED)
        cosine = ax.plot(np.cos, color=BLUE)
        self.play(
            FadeIn(ax, sine, cosine)
        )
       
        red_square = Square(fill_opacity=1, side_length=0.5, fill_color=RED_C).to_corner(UL)
        blue_square = Square(fill_opacity=1, side_length=0.5, fill_color=BLUE_C).to_corner(UL - DOWN)

        self.play(DrawBorderThenFill(red_square))
        self.play(DrawBorderThenFill(blue_square))
        text_sin = MathTex(r"\sin(x)")
        text_cos = MathTex(r"\cos(x)")
        text_sin.next_to(Square(fill_opacity=1, side_length=0.5, fill_color=RED_C).to_corner(UL))
        text_cos.next_to(Square(fill_opacity=1, side_length=0.5, fill_color=BLUE_C).to_corner(UL - DOWN))
        # Correct usage of next_to: Multiply RIGHT by a scala

        self.play(Write(text_sin))
        self.wait(0.5)
        self.play(Write(text_cos))
        self.wait(0.5)
        self.wait(8)
        self.play(FadeOut(sine, cosine, text_sin, text_cos, ax, red_square, blue_square))
        self.wait(2)

        prob_cos = Tex(r"Prove that $\cos\left(x - \frac{\pi}{2}\right)$ is the same as $\sin x$")
        self.play(Write(prob_cos))
        self.wait(2)
        self.play(
            Transform(prob_cos, prob_cos.copy().to_corner(UP))
        )
        self.wait(10)

        step1 = Tex(r"1. Make balance equation $\cos\left(x - \frac{\pi}{2}\right) = \sin x$")
        step2 = Tex("2. Identify which side is easier to change form, or simplify.")
        step3 = Tex("3. Formulate and make it equal to the other side.")

        steps = VGroup(step1, step2, step3).arrange(DOWN, aligned_edge=LEFT)
        steps.move_to(ORIGIN)
        steps.next_to(prob_cos, DOWN, buff=0.5)

        self.play(
            Write(steps)
        )
        self.wait(3)
        self.play(Circumscribe(step1, Rectangle, time_width=4))
        self.play(
            FadeOut(step2, step3)
        )
        step1_exp = MathTex(r"\cos\left(x-\frac{\pi}{2}\right) = \sin x")
        step1_exp.move_to(ORIGIN)
        self.play(
            Write(step1_exp)
        )
        self.wait(6)
        self.play(
            FadeOut(step1, step1_exp),
        )
        self.wait(1)
        self.play(
            FadeIn(steps),
        )
        self.wait(3)
        self.play(
            Circumscribe(step2, Rectangle, time_width=4)
        )
        self.play(
            FadeOut(step1, step3),
            Transform(step2, step2.copy().shift(UP))
        )
        self.wait(3)

        step2_exp = MathTex(r"\cos\left(x-\frac{\pi}{2}\right)", color=BLUE)
        step2_exp.move_to(ORIGIN)
        self.wait(2)
        self.play(Write(step2_exp))
        self.wait(4)
        self.play(
            Transform(step2, step2.copy().shift(DOWN)),
            FadeOut(step2_exp)
        )
        self.play(FadeIn(step1, step3))
        self.wait(1)
        self.wait(2)
        self.play(
            Circumscribe(step3, Rectangle, time_width=4)
        )
        self.play(
            FadeOut(step1, step2),
            Transform(step3, step3.copy().shift(UP + UP))
        )
        self.wait(3)
        step3_exp = MathTex(r"\cos\left(x-\frac{\pi}{2}\right) = \cos(x) \cos\left(\frac{\pi}{2}\right) + \sin(x) \sin\left(\frac{\pi}{2}\right)")
        step3_exp.move_to(ORIGIN)
        
        # --- Modified highlighted section begins here ---
        parts = VGroup(*step3_exp.get_parts_by_tex(["=", r"\cos", r"\sin", "+"]))
        self.play(AnimationGroup(
            *[FadeIn(part, shift=UP * 0.5) for part in parts],
            lag_ratio=0.2
        ))
        self.wait(2)

        step3_exp2 = MathTex(r"= \cos(x) \cdot 0 + \sin(x) \cdot 1")
        step3_exp2.next_to(step3_exp, DOWN)
        self.play(
            TransformFromCopy(step3_exp, step3_exp2),
            run_time=1.5
        )
        self.wait(2)

        step3_exp3 = MathTex(r"= 0 + \sin(x)")
        step3_exp3.next_to(step3_exp2, DOWN)
        self.play(
            ReplacementTransform(step3_exp2.copy(), step3_exp3),
            run_time=1.5
        )
        self.wait(2)

        step3_exp4 = MathTex(r"= \sin(x)")
        step3_exp4.next_to(step3_exp3, DOWN)
        self.play(
            TransformMatchingShapes(step3_exp3.copy(), step3_exp4),
            run_time=1.5
        )
        self.wait(2)

        # Create highlighting effect with pulsing animation
        self.play(
            *[exp.animate.scale(1.2, rate_func=there_and_back) for exp in [step3_exp, step3_exp2, step3_exp3, step3_exp4]],
            *[exp.animate.set_color(YELLOW) for exp in [step3_exp, step3_exp2, step3_exp3, step3_exp4]],
            run_time=2
        )
        self.wait(1)

        # Smooth transition with spiral effect
        self.play(
            *[FadeOut(exp, shift=LEFT) for exp in [step3_exp, step3_exp2, step3_exp3]],
            step3_exp4.animate.move_to(ORIGIN).scale(1.2),
            run_time=1.5
        )
        self.wait(2)

        final_proof = Tex(r"Therefore, $\cos\left(x - \frac{\pi}{2}\right) = \sin x$ is proven.")
        final_proof.next_to(step3_exp4, DOWN)
        
        # Create dramatic reveal for final proof
        self.play(
            Write(final_proof, run_time=2),
            Flash(final_proof, color=BLUE, flash_radius=0.5),
            step3_exp4.animate.set_color(GREEN)
        )
        self.wait(5)

        # Final emphasis animation
        self.play(
            Indicate(final_proof, color=YELLOW, scale_factor=1.2),
            run_time=2
        )
        # --- Modified highlighted section ends here ---

        self.play(
            FadeOut(final_proof, step3, step3_exp4, prob_cos)
        )

        # Create axes and graphs
        ax = Axes(
            x_range=[-2*PI, 2*PI, PI/2],
            y_range=[-2, 2, 1],
            x_length=10,
            y_length=6,
        )

        # Plot sin and cos
        sine = ax.plot(lambda x: np.sin(x), color=RED)
        cosine = ax.plot(lambda x: np.cos(x), color=BLUE)

        # Labels
        sin_label = MathTex(r"\sin(x)", color=RED).next_to(ax, UP)
        cos_label = MathTex(r"\cos(x)", color=BLUE).next_to(sin_label, RIGHT)

        # Add everything to scene
        self.play(Create(ax))
        self.play(
            Create(sine),
            Create(cosine),
            Write(sin_label),
            Write(cos_label)
        )
        self.wait(2)

        # Show translation
        shift_text = Tex(r"Shifting $\cos(x)$ left by $\frac{\pi}{2}$ gives us $\sin(x)$").to_edge(UP)
        self.play(
            Write(shift_text),
            FadeOut(sin_label, cos_label)
        )

        # Create shifted cosine
        shifted_cosine = ax.plot(
            lambda x: np.cos(x - PI/2),
            color=GREEN
        )

        shifted_label = MathTex(r"\cos(x-\frac{\pi}{2})", color=GREEN).next_to(ax, DOWN)

        translated_cosine = VGroup(shifted_cosine, shifted_label)

        # Animate the shift
        self.play(
            Transform(
                cosine,
                shifted_cosine
            ),
            Write(shifted_label)
        )

        # Fade out the original cosine graph
        self.play(FadeOut(cosine))
        self.wait(0.5)

        # Cleanup
        self.play(
            FadeOut(ax, sine, shift_text, translated_cosine)
        )
        
        self.wait(3)
