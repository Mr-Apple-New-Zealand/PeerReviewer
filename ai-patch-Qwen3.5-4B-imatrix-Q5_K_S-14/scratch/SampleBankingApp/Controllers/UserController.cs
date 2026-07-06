using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Services;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class UserController : ControllerBase
{
    private readonly UserService _userService;
    private readonly ILogger<UserController> _logger;

    public UserController(UserService userService, ILogger<UserController> logger)
    {
        _userService = userService;
        _logger = logger;
    }

    [HttpGet("{id}")]
    public IActionResult GetUser(int id)
    {
        var user = _userService.GetUserById(id);
        if (user == null)
            return NotFound();

        return Ok(user);
    }

    [HttpGet]
    public IActionResult GetUsers([FromQuery] int page = 1, [FromQuery] int pageSize = 20)
    {
        var users = _userService.GetUsersPage(page, pageSize);
        return Ok(users);
    }

    [HttpPut("{id}")]
    public IActionResult UpdateUser(int id, [FromBody] UpdateUserRequest request)
    {
        if (request == null)
            return BadRequest(new { message = "Request body is required" });

        if (id <= 0)
            return BadRequest(new { message = "Invalid user ID" });

        try
        {
            _userService.UpdateUser(id, request.Email, request.Username);
            return NoContent();
        }
        catch (ArgumentException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating user {Id}", id);
            return StatusCode(500, "An error occurred while updating user");
        }
    }

    [HttpDelete("{id}")]
    public IActionResult DeleteUser(int id)
    {
        if (id <= 0)
            return BadRequest(new { message = "Invalid user ID" });

        try
        {
            _userService.DeleteUser(id);
            return NoContent();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting user {Id}", id);
            return StatusCode(500, "An error occurred while deleting user");
        }
    }

    [HttpGet("search")]
    public IActionResult SearchUsers([FromQuery] string query)
    {
        if (string.IsNullOrWhiteSpace(query))
            return BadRequest(new { message = "Search query is required" });

        var results = _userService.SearchUsers(query);
        return Ok(results);
    }

    [HttpGet("audit")]
    public IActionResult GetAuditLog()
    {
        return Ok(_userService.GetAuditReport());
    }
}

public class UpdateUserRequest
{
    public string Email { get; set; } = string.Empty;
    public string Username { get; set; } = string.Empty;
}
