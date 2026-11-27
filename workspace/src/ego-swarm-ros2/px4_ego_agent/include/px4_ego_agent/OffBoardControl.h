//
// Created by tlab-uav on 25-3-5.
//

#ifndef OFFBOARDCONTROL_H
#define OFFBOARDCONTROL_H
#include <px4_msgs/msg/offboard_control_mode.hpp>
#include <px4_msgs/msg/trajectory_setpoint.hpp>
#include <px4_msgs/msg/vehicle_command.hpp>
#include <quadrotor_msgs/msg/position_command.hpp>
#include <rclcpp/rclcpp.hpp>


class OffBoardControl
{
public:
    explicit OffBoardControl(rclcpp::Node::SharedPtr node);
    ~OffBoardControl() = default;

    void takeOff(float height);
    void land() const;
    void disarm() const;
protected:
    rclcpp::Node::SharedPtr node_;
    rclcpp::TimerBase::SharedPtr timer_;

    void arm() const;
    void publishOffBoardControlMode();
    void publishTrajectorySetpoint();
    void publishVehicleCommand(uint16_t command, float param1 = 0.0, float param2 = 0.0) const;

    /// @brief Callback for planner position commands — updates target_ for trajectory following
    void positionCmdCallback(const quadrotor_msgs::msg::PositionCommand::SharedPtr msg);

    px4_msgs::msg::TrajectorySetpoint target_{};
    long system_id_;

    /// @brief Whether a valid planning position command has been received
    bool planning_cmd_received_{false};
    /// @brief Timestamp of the last received position command
    rclcpp::Time last_planning_cmd_time_;

    rclcpp::Publisher<px4_msgs::msg::OffboardControlMode>::SharedPtr offboard_control_mode_publisher_;
    rclcpp::Publisher<px4_msgs::msg::TrajectorySetpoint>::SharedPtr trajectory_setpoint_publisher_;
    rclcpp::Publisher<px4_msgs::msg::VehicleCommand>::SharedPtr vehicle_command_publisher_;
    rclcpp::Subscription<quadrotor_msgs::msg::PositionCommand>::SharedPtr planning_pos_cmd_sub_;
};


#endif //OFFBOARDCONTROL_H
